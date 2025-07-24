import os
import yaml
import json
import requests
import logging
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
from time import sleep
from typing import Tuple, Optional
from tenacity import retry, stop_after_attempt, before_sleep_log, wait_exponential

# Local imports
from xcelEndpoint import xcelEndpoint

IEEE_PREFIX = '{urn:ieee:std:2030.5:ns}'

logger = logging.getLogger(__name__)

class xcelMeter():

    def __init__(self, name: str, ip_address: str, port: int, creds: Optional[Tuple[str, str]] = None):
        self.name = name
        self.POLLING_RATE = 5.0  # Poll every 5 seconds
        # Base URL used to query the meter - use HTTP for simulator
        self.url = f'http://{ip_address}:{port}'

        # Setup the MQTT server connection
        # Use 'localhost' for local development, 'mqtt' for Docker
        mqtt_server = os.environ.get('MQTT_SERVER', 'localhost')
        # If running in Docker, use 'mqtt' service name, otherwise use 'localhost'
        if mqtt_server == 'mqtt' and not os.environ.get('DOCKER_ENV'):
            mqtt_server = 'localhost'
        
        self.mqtt_server_address = mqtt_server
        self.mqtt_port = int(os.environ.get('MQTT_PORT', '1883'))
        
        print(f"MQTT Configuration:")
        print(f"  Server: {self.mqtt_server_address}")
        print(f"  Port: {self.mqtt_port}")
        
        self.mqtt_client = self.setup_mqtt(self.mqtt_server_address, self.mqtt_port)

        # Create a new requests session - simplified for simulator
        self.requests_session = self.setup_session(creds, ip_address)

        # Set to uninitialized
        self.initalized = False

    @retry(stop=stop_after_attempt(15),
           wait=wait_exponential(multiplier=1, min=1, max=15),
           before_sleep=before_sleep_log(logger, logging.WARNING),
           reraise=True)
    def setup(self) -> None: # This method initializes, or creates a meter object
        # XML Entries we're looking for within the endpoint
        hw_info_names = ['sFDI', 'swVer', 'mfID']
        # Endpoint of the meter used for HW info
        hw_info_url = '/sdev' # e.g. http://localhost:8082/sdev or http://<IP_ADDRESS>:8082/sdev
        # Query the meter to get some more details about it
        details_dict = self.get_hardware_details(hw_info_url, hw_info_names)
        self._mfid = details_dict.get('mfID', 'Unknown')
        self._sfdi = details_dict.get('sFDI', 'Unknown')
        self._swVer = details_dict.get('swVer', 'Unknown')

        # Device info used for home assistant MQTT discovery
        self.device_info = {
                            "device": {
                                "identifiers": [self._sfdi],
                                "name": self.name,
                                "model": self._mfid,
                                "sw_version": self._swVer
                                }
                            }
        # Send homeassistant a new device config for the meter
        self.send_mqtt_config()

        # The swVer will dictate which version of endpoints we use
        endpoints_file_ver = 'default' if str(self._swVer) != '3.2.39' else '3_2_39'
        # List to store our endpoint objects in
        self.endpoints_list = self.load_endpoints(f'configs/endpoints_{endpoints_file_ver}.yaml')

        # create endpoints from list
        self.endpoints = self.create_endpoints(self.endpoints_list, self.device_info)

        # ready to go
        self.initalized = True

    def get_hardware_details(self, hw_info_url: str, hw_names: list) -> dict:
        """
        Queries the meter hardware endpoint at the ip address passed
        to the class.

        Returns: dict, {<element name>: <meter response>}
        """
        query_url = f'{self.url}{hw_info_url}'
        # query the hw specs endpoint
        x = self.requests_session.get(query_url, timeout=4.0)
        
        print(f"Device info response from {query_url}:")
        print(f"Status: {x.status_code}")
        print(f"Content: {x.text}")
        
        # Parse the response xml looking for the passed in element names
        root = ET.fromstring(x.text)
        hw_info_dict = {}
        for name in hw_names:
            element = root.find(f'.//{IEEE_PREFIX}{name}')
            if element is not None and element.text is not None:
                hw_info_dict[name] = element.text
                print(f"Found {name}: {element.text}")
            else:
                hw_info_dict[name] = 'Unknown'
                print(f"Missing {name}, using default")

        return hw_info_dict

    @staticmethod
    def setup_session(creds: Optional[tuple], ip_address: str) -> requests.Session:
        """
        Creates a new requests session - simplified for simulator (no SSL required)
        
        Returns: request.session
        """
        session = requests.Session()
        
        # For simulator, no SSL certificates needed
        if creds:
            session.cert = creds
        
        return session

    @staticmethod
    def load_endpoints(file_path: str) -> list:
        """
        Loads the yaml file passed containing meter endpoint information

        Returns: list
        """
        with open(file_path, mode='r', encoding='utf-8') as file:
            endpoints = yaml.safe_load(file)

        return endpoints

    def create_endpoints(self, endpoints: dict, device_info: dict) -> None:
        # Build query objects for each endpoint
        query_obj = []
        for point in endpoints:
            for endpoint_name, v in point.items():
                request_url = f'{self.url}{v["url"]}'
                query_obj.append(xcelEndpoint(self.requests_session, self.mqtt_client,
                                    request_url, endpoint_name, v['tags'], device_info))

        return query_obj

    @staticmethod
    def get_mqtt_port() -> int:
        """
        Identifies the port to use for the MQTT server. Very basic,
        just offers a default of 1883 if no other port is set

        Returns: int
        """
        env_port = os.getenv('MQTT_PORT')
        # If environment variable for MQTT port is set, use that
        # if not, use the default
        mqtt_port = int(env_port) if env_port else 1883

        return mqtt_port

    @staticmethod
    def setup_mqtt(mqtt_server_address, mqtt_port) -> mqtt.Client:
        """
        Creates a new mqtt client to be used for the the xcelQuery
        objects.

        Returns: mqtt.Client object
        """
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.info("Connected to MQTT Broker!")
            else:
                logging.error("Failed to connect, return code %d\n", rc)

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                logging.warning("Unexpected MQTT disconnection. Attempting to reconnect...")

        # Check if a username/PW is setup for the MQTT connection
        mqtt_username = os.getenv('MQTT_USER')
        mqtt_password = os.getenv('MQTT_PASSWORD')
        
        print(f"Connecting to MQTT broker at {mqtt_server_address}:{mqtt_port}")
        if mqtt_username:
            print(f"Using MQTT credentials: {mqtt_username}")
        
        # Create client with persistent connection settings
        client = mqtt.Client(client_id="meter2mqtt_client", clean_session=False)
        if mqtt_username and mqtt_password:
            client.username_pw_set(mqtt_username, mqtt_password)
        
        # Set connection parameters for better stability
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        
        # Enable automatic reconnection
        client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        try:
            client.connect(mqtt_server_address, mqtt_port, keepalive=60)
            client.loop_start()
            print("MQTT client setup completed successfully")
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            raise

        return client

    # Send MQTT config setup to Home assistant
    def send_configs(self):
        """
        Sends the MQTT config to the homeassistant topic for
        automatic discovery

        Returns: None
        """
        for obj in self.query_obj:
            obj.mqtt_send_config()
            input()

    def send_mqtt_config(self) -> None:
        """
        Sends a discovery payload to homeassistant for the new meter device

        - sends device information ( a.k.a discovery payload) to a topic "homeassistant/device/energy/xcel_itron_5" 
        
        Returns: None
        """

        # {self.name.replace(" ", "_").lower() creates xcel_itron_5 from Xcel Itron 5 to make homeassistant/device/energy/xcel_itron_5
        state_topic = f'homeassistant/device/energy/{self.name.replace(" ", "_").lower()}' 
        logging.info(f"MQTT Discovery Topic being used: {state_topic}")  # <-- Added logging here
        config_dict = {
            "name": self.name,
            "device_class": "energy",
            "state_topic": state_topic,
            "unique_id": self._sfdi
            }
        config_dict.update(self.device_info)
        config_json = json.dumps(config_dict)
        logging.debug(f"")
        logging.debug(f"")
        logging.debug(f"Sending MQTT Discovery Payload")
        logging.debug(f"")
        logging.debug(f"")
        logging.debug(f"TOPIC: {state_topic}")
        logging.debug(f"")
        logging.debug(f"")
        logging.debug(f"MESSAGE: {config_json}")
        logging.debug(f"")
        logging.debug(f"")
        logging.info(f"Formatted JSON Structure of Message ( DEVICE INFO): {json.dumps(config_dict, indent=2)}")
        logging.debug(f"")
        logging.debug(f"")
        logging.info(f"Publishing to topic: {state_topic}")  # <-- Log topic before publish

        # JUST NEED TO CUSTOMIZE PUBLISH METHOD!
        self.mqtt_client.publish(state_topic, str(config_json))

    def run(self) -> None:
        """
        Main business loop. Just repeatedly queries the meter endpoints,
        parses the results, packages these up into MQTT payloads, and sends
        them off to the MQTT server

        Returns: None
        """
        while True:
            sleep(self.POLLING_RATE)
            for obj in self.endpoints:
                obj.run()
