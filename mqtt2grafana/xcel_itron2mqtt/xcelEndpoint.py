import yaml
import os
import json
import requests
import logging
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
from copy import deepcopy
from tenacity import retry, stop_after_attempt, before_sleep_log, wait_exponential

logger = logging.getLogger(__name__)

# Prefix that appears on all of the XML elements
IEEE_PREFIX = '{urn:ieee:std:2030.5:ns}'

class xcelEndpoint():
    """
    Class wrapper for all readings associated with the Xcel meter.
    Expects a request session that should be shared amongst the 
    instances.
    """
    def __init__(self, session: requests.Session, mqtt_client: mqtt.Client, 
                    url: str, name: str, tags: list, device_info: dict):
        self.requests_session = session
        self.url = url
        self.name = name
        self.tags = tags
        self.client = mqtt_client
        self.device_info = device_info

        # Get meter-specific topic prefix
        meter_id = os.getenv('METER_ID', 'meter_001')
        self._mqtt_topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant/')
        self._meter_topic_prefix = f"xcel_itron5_{meter_id}"
        self._current_response = None
        self._mqtt_topic = None
        # Record all of the sensor state topics in an easy to lookup dict
        self._sensor_state_topics = {}

        # Setup the rest of what we need for this endpoint
        self.mqtt_send_config()

    @retry(stop=stop_after_attempt(15),
           wait=wait_exponential(multiplier=1, min=1, max=15),
           before_sleep=before_sleep_log(logger, logging.WARNING),
           reraise=True)
    def query_endpoint(self) -> str:
        """
        Sends a request to the given endpoint associated with the 
        object instance

        Returns: str in XML format of the meter's response
        """
        x = self.requests_session.get(self.url, verify=False, timeout=15.0)
    
        return x.text

    @staticmethod
    def parse_response(response: str, tags: dict) -> dict:
        """
        Drill down the XML response from the meter and extract the
        readings according to the endpoints.yaml structure.

        Returns: dict in the nesting structure of found below each tag
        in the endpoints.yaml
        """
        readings_dict = {}
        root = ET.fromstring(response)
        # Kinda gross
        for k, v in tags.items():
            if isinstance(v, list):
                for val_items in v:
                    for k2, v2 in val_items.items():
                        search_val = f'{IEEE_PREFIX}{k2}'
                        if root.find(f'.//{search_val}') is not None:
                            value = root.find(f'.//{search_val}').text
                            readings_dict[f'{k}{k2}'] = value
            else:
                search_val = f'{IEEE_PREFIX}{k}'
                if root.find(f'.//{IEEE_PREFIX}{k}') is not None:
                    value = root.find(f'.//{IEEE_PREFIX}{k}').text
                    readings_dict[k] = value
    
        return readings_dict

    def get_reading(self) -> dict:
        """
        Query the endpoint associated with the object instance and
        return the parsed XML response in the form of a dictionary
        
        Returns: Dict in the form of {reading: value}
        """
        logging.info(f"L90 => XcelEndpoint() =>get_reading() Querying URL: {self.url}")
        logging.info(f"L91 => XcelEndpoint() =>get_reading() Endpoint name: {self.name}")
        logging.info(f"L92 => XcelEndpoint() =>get_reading() Endpoint tags: {self.tags}\n\n")
        # logging.info("=" * 80)

        response = self.query_endpoint()
        logging.info(f"="*80)  # Log first 500 chars
        logging.info(f"L97 => XcelEndpoint() =>get_reading() => Response preview (first 500 chars):\n")
        logging.info(f"{response[:500]}")

        self.current_response = self.parse_response(response, self.tags)

        return self.current_response

    def create_config(self, sensor_name: str,  details: dict) -> tuple[str, dict]:
        """
        Helper to generate the JSON sonfig payload for setting
        up the new Homeassistant entities

        Returns: Tuple consisting of a string representing the mqtt
        topic, and a dict to be used as the payload.
        """
        payload = deepcopy(details)
        mqtt_friendly_name = self.name.replace(" ", "_")
        entity_type = payload.pop('entity_type')

        # Use meter-specific topic prefix for state topics
        payload["state_topic"] = f'{self._meter_topic_prefix}/{entity_type}/{mqtt_friendly_name}/{sensor_name}/state'
        payload['name'] = f'{self.name} {sensor_name}'
        # Mouthful
        # Unique ID becomes the device name + class name + sensor name, all lower case, all underscores instead of spaces
        payload['unique_id'] = f"{self.device_info['device']['name']}_{self.name}_{sensor_name}".lower().replace(' ', '_')
        payload.update(self.device_info)
        # MQTT Topics don't like spaces - use meter-specific prefix for config topics too
        mqtt_topic = f'{self._meter_topic_prefix}/{entity_type}/{mqtt_friendly_name}/{sensor_name}/config'
        # Capture the state topic the sensor is associated with for later use
        self._sensor_state_topics[sensor_name] = payload['state_topic']

       
        # logging.info(f"=====================================================================================================")
        logging.info(f"==================================xcelEndPoint()======================================================")
        # logging.info(f"======================================================================================================")
        logging.info(f"L130 XcelEndpoint() => create_config() MQTT TOPIC: {mqtt_topic}\n")
        logging.info(f"L131 XcelEndpoint() => create_config() PAYLOAD: {payload}\n")
        # logging.info(f"L132 XcelEndpoint() => create_config() Sensor Name: {sensor_name}\n")
        # logging.info(f"L133 XcelEndpoint() => create_config() Creating MQTT config for {sensor_name} with topic {mqtt_topic} and payload: {payload}\n")

        payload = json.dumps(payload)

        return mqtt_topic, payload

    def mqtt_send_config(self) -> None:
        """
        Homeassistant requires a config payload to be sent to more
        easily setup the sensor/device once it appears over mqtt
        https://www.home-assistant.io/integrations/mqtt/
        """

        _tags = deepcopy(self.tags)
        for k, v in _tags.items():
            if isinstance(v, list):
                for val_items in v:
                    name, details = val_items.popitem()
                    sensor_name = f'{k}{name}'
                    mqtt_topic, payload = self.create_config(sensor_name, details)

                    # Send MQTT payload
                    publish_result = self.mqtt_publish(
                        mqtt_topic, str(payload))

            else:
                name_suffix = f'{k[0].upper()}'
                mqtt_topic, payload = self.create_config(k, v)

                publish_result = self.mqtt_publish(
                    mqtt_topic, str(payload), retain=True)

                logging.info(f"Publish result: {publish_result}")
                # logging.info("=" * 80)

    def process_send_mqtt(self, reading: dict) -> None:
        """
        Run through the readings from the meter and translate
        and prepare these readings to send over mqtt

        Returns: None
        """

        # logging.debug(f"READINGS FROM METER => XcelEndpoint L160: {reading}\n\n\n")

        mqtt_topic_message = {}
        # Cycle through all the readings for the given sensor
        for k, v in reading.items():

            # Figure out which topic this reading needs to be sent to
            topic = self._sensor_state_topics[k]
            if topic not in mqtt_topic_message.keys():
                mqtt_topic_message[topic] = {}
            # Create dict of {topic: payload}
            mqtt_topic_message[topic] = v
        
        # logging.info(f"L189 XcelEndpoint() => process_send_mqtt() mqtt_topic_message topic and value pair :\n")
        # logging.info(f"{json.dumps(mqtt_topic_message, indent=4)}")

        """
          An example of the mqtt_topic_message dict :

          mqtt_topic_message  = {
                "homeassistant/sensor/Current_Summation_Delivered/timePeriodduration/state": "1",
                "homeassistant/sensor/Current_Summation_Delivered/timePeriodstart/state": "1753820381",
                "homeassistant/sensor/Current_Summation_Delivered/touTier/state": "0",
                "homeassistant/sensor/Current_Summation_Delivered/value/state": "15272525"}
         """
         # Cycle through and send the payload to the associated key
        for topic, payload in mqtt_topic_message.items():
            publish_result = self.mqtt_publish(topic, payload)
        
        # # publish only homeassistant/sensor/Current_Summation_Delivered/value/state ( I care about publishing only )
        # last_topic, last_payload = list(mqtt_topic_message.items())[-1]
        # publish_result = self.mqtt_publish(last_topic, last_payload)


        

    def mqtt_publish(self, topic: str, message: str, retain=False) -> int:
        """
        Publish the given message to the topic associated with the class
       
        Returns: integer
        """
        result = [0]
        
        # logging.info(f"L220 xcelEndPoint() => mqtt_publish() at Topic: '{topic}'\n")
        
        logging.info(f"L222 xcelEndPoint() => mqtt_publish() Published message: '{message}' at {topic}\n'")
    
        logging.info(f"===============================================L224 END OF LOOOP!!!!!!!!!!!=====================================================================================\n\n\n\n")

        result = self.client.publish(topic, str(message), retain=retain)
        return result[0]

    def run(self) -> None:
        """
        Main business loop for the endpoint class.
        Read from the meter, process and send over MQTT

        Returns: None
        """

        reading = self.get_reading()
        self.process_send_mqtt(reading)

    
