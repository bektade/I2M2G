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

        self._mqtt_topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant/')
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
        # DEBUGGING: Add detailed logging for get_reading method
        # logging.info("=" * 80)
        # logging.info("DEBUGGING GET_READING IN xcelEndpoint.py")
        # logging.info("=" * 80)
        logging.info(f"L94 => XcelEndpoint() =>get_reading() Querying URL: {self.url}")
        logging.info(f"L94 => XcelEndpoint() =>get_reading() Endpoint name: {self.name}")
        logging.info(f"L94 => XcelEndpoint() =>get_reading() Endpoint tags: {self.tags}")
        # logging.info("=" * 80)

        response = self.query_endpoint()

        # DEBUGGING: Add detailed logging after query_endpoint
        # logging.info("=" * 80)
        # logging.info(
        #     "DEBUGGING AFTER QUERY_ENDPOINT IN xcelEndpoint.py get_reading()")
        # logging.info("=" * 80)
        # logging.info(f"Response type: {type(response)}")
        # logging.info(f"Response length: {len(response)} characters")
        logging.info(f"\n\nL108 => XcelEndpoint() =>get_reading() => Response preview (first 1000 chars): {response[:1000]}")
        # logging.info("=" * 80)

        self.current_response = self.parse_response(response, self.tags)

        # DEBUGGING: Add detailed logging after parse_response
        # logging.info("=" * 80)
        # logging.info(
        #     "DEBUGGING AFTER PARSE_RESPONSE IN xcelEndpoint.py get_reading()")
        # logging.info("=" * 80)
        # logging.info(f"Parsed response: {self.current_response}")
        # logging.info(f"Parsed response type: {type(self.current_response)}")
        # logging.info(
        #     f"Parsed response keys: {list(self.current_response.keys()) if isinstance(self.current_response, dict) else 'Not a dict'}")
        # logging.info("=" * 80)

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
        payload["state_topic"] = f'{self._mqtt_topic_prefix}{entity_type}/{mqtt_friendly_name}/{sensor_name}/state'
        payload['name'] = f'{self.name} {sensor_name}'
        # Mouthful
        # Unique ID becomes the device name + class name + sensor name, all lower case, all underscores instead of spaces
        payload['unique_id'] = f"{self.device_info['device']['name']}_{self.name}_{sensor_name}".lower().replace(' ', '_')
        payload.update(self.device_info)
        # MQTT Topics don't like spaces
        mqtt_topic = f'{self._mqtt_topic_prefix}{entity_type}/{mqtt_friendly_name}/{sensor_name}/config'
        # Capture the state topic the sensor is associated with for later use
        self._sensor_state_topics[sensor_name] = payload['state_topic']

       
        logging.info(f"=========================================================")
        logging.info(f"L150 XcelEndpoint() => create_config() MQTT TOPIC: {mqtt_topic}\n")
        logging.info(f"L151 XcelEndpoint() => create_config() PAYLOAD: {payload}\n")
        logging.info(f"L152 XcelEndpoint() => create_config() Sensor Name: {sensor_name}\n")
        logging.info(f"L153 XcelEndpoint() => create_config() Creating MQTT config for {sensor_name} with topic {mqtt_topic} and payload: {payload}\n")

        payload = json.dumps(payload)

        return mqtt_topic, payload

    def mqtt_send_config(self) -> None:
        """
        Homeassistant requires a config payload to be sent to more
        easily setup the sensor/device once it appears over mqtt
        https://www.home-assistant.io/integrations/mqtt/
        """
        # logging.info("=" * 80)
        # logging.info(
        #     "DEBUGGING MQTT CONFIG SEND IN xcelEndpoint.py mqtt_send_config()")
        # logging.info("=" * 80)
        # logging.info(f"Self tags: {self.tags}")
        # logging.info(f"Self name: {self.name}")
        # logging.info(f"Self device_info: {self.device_info}")
        # logging.info("=" * 80)

        _tags = deepcopy(self.tags)
        for k, v in _tags.items():
            if isinstance(v, list):
                for val_items in v:
                    name, details = val_items.popitem()
                    sensor_name = f'{k}{name}'
                    mqtt_topic, payload = self.create_config(sensor_name, details)

                    # DEBUGGING: Add detailed logging before MQTT config publish
                    # logging.info("=" * 80)
                    # logging.info(
                    #     "DEBUGGING MQTT CONFIG PUBLISH IN xcelEndpoint.py mqtt_send_config()")
                    # logging.info("=" * 80)
                    # logging.info(f"Sensor name: {sensor_name}")
                    # logging.info(f"MQTT topic: {mqtt_topic}")
                    # logging.info(f"Payload type: {type(payload)}")
                    # logging.info(f"Payload value: {payload}")
                    # logging.info(f"Payload length: {len(payload)} characters")
                    # logging.info("=" * 80)

                    # Send MQTT payload
                    publish_result = self.mqtt_publish(
                        mqtt_topic, str(payload))

                    # DEBUGGING: Add detailed logging after MQTT config publish
                    # logging.info("=" * 80)
                    # logging.info(
                    #     "MQTT CONFIG PUBLISH RESULT IN xcelEndpoint.py mqtt_send_config()")
                    # logging.info("=" * 80)
                    # logging.info(f"Publish result: {publish_result}")
                    # logging.info("=" * 80)
            else:
                name_suffix = f'{k[0].upper()}'
                mqtt_topic, payload = self.create_config(k, v)

                # DEBUGGING: Add detailed logging before MQTT config publish (retain=True)
                # logging.info("=" * 80)
                # logging.info(
                #     "DEBUGGING MQTT CONFIG PUBLISH (RETAIN) IN xcelEndpoint.py mqtt_send_config()")
                # logging.info("=" * 80)
                # logging.info(f"Key: {k}")
                # logging.info(f"MQTT topic: {mqtt_topic}")
                # logging.info(f"Payload type: {type(payload)}")
                # logging.info(f"Payload value: {payload}")
                # logging.info(f"Payload length: {len(payload)} characters")
                # logging.info(f"Retain flag: True")
                # logging.info("=" * 80)

                publish_result = self.mqtt_publish(
                    mqtt_topic, str(payload), retain=True)

                # DEBUGGING: Add detailed logging after MQTT config publish (retain=True)
                # logging.info("=" * 80)
                # logging.info(
                #     "MQTT CONFIG PUBLISH RESULT (RETAIN) IN xcelEndpoint.py mqtt_send_config()")
                # logging.info("=" * 80)
                logging.info(f"Publish result: {publish_result}")
                # logging.info("=" * 80)

    def process_send_mqtt(self, reading: dict) -> None:
        """
        Run through the readings from the meter and translate
        and prepare these readings to send over mqtt

        Returns: None
        """

        # logging.debug(f"READINGS FROM METER => XcelEndpoint L160: {reading}\n\n\n")

        # DEBUGGING: Add detailed logging for process_send_mqtt
        # logging.info("=" * 80)
        # logging.info("DEBUGGING PROCESS_SEND_MQTT IN xcelEndpoint.py")
        # logging.info("=" * 80)
        # logging.info(f"Reading dict: {reading}")
        # logging.info(f"Reading dict type: {type(reading)}")
        # logging.info(f"Reading dict keys: {list(reading.keys())}")
        # logging.info(f"Self _sensor_state_topics: {self._sensor_state_topics}")
        # logging.info("=" * 80)

        mqtt_topic_message = {}
        # Cycle through all the readings for the given sensor
        for k, v in reading.items():
            # DEBUGGING: Add detailed logging for each reading processing
            # logging.info("=" * 80)
            # logging.info(
            #     "DEBUGGING READING PROCESSING IN xcelEndpoint.py process_send_mqtt()")
            # logging.info("=" * 80)
            # logging.info(f"Processing key: {k}, value: {v}")
            # logging.info(f"Value type: {type(v)}")
            # logging.info(
            #     f"Looking for topic in _sensor_state_topics for key: {k}")
            # logging.info("=" * 80)

            # Figure out which topic this reading needs to be sent to
            topic = self._sensor_state_topics[k]
            if topic not in mqtt_topic_message.keys():
                mqtt_topic_message[topic] = {}
            # Create dict of {topic: payload}
            mqtt_topic_message[topic] = v

            # DEBUGGING: Add detailed logging for topic assignment
            # logging.info("=" * 80)
            # logging.info(
            #     "DEBUGGING TOPIC ASSIGNMENT IN xcelEndpoint.py process_send_mqtt()")
            # logging.info("=" * 80)
            # logging.info(f"Assigned topic: {topic}")
            # logging.info(f"Current mqtt_topic_message: {mqtt_topic_message}")
            # logging.info("=" * 80)

        # Cycle through and send the payload to the associated keys

        # logging.debug(f"MQTT TOPIC MESSAGE: {mqtt_topic_message}\n\n\n")
        # logging.debug(f"MQTT TOPIC MESSAGE KEYS: {mqtt_topic_message.keys()}\n")

        # DEBUGGING: Add detailed logging before sending messages
        # logging.info("=" * 80)
        # logging.info(
        #     "DEBUGGING FINAL MQTT MESSAGE SEND IN xcelEndpoint.py process_send_mqtt()")
        # logging.info("=" * 80)
        # logging.info(f"Final mqtt_topic_message: {mqtt_topic_message}")
        # logging.info(f"Number of topics to publish: {len(mqtt_topic_message)}")
        # logging.info("=" * 80)

        for topic, payload in mqtt_topic_message.items():
            # DEBUGGING: Add detailed logging for each message publish
            # logging.info("=" * 80)
            # logging.info(
            #     "DEBUGGING MESSAGE PUBLISH IN xcelEndpoint.py process_send_mqtt()")
            # logging.info("=" * 80)
            # logging.info(f"Publishing to topic: {topic}")
            # logging.info(f"Payload: {payload}")
            # logging.info(f"Payload type: {type(payload)}")
            # logging.info(f"Payload length: {len(str(payload))} characters")
            # logging.info("=" * 80)

            publish_result = self.mqtt_publish(topic, payload)

            # DEBUGGING: Add detailed logging after each message publish
            # logging.info("=" * 80)
            # logging.info(
            #     "DEBUGGING MESSAGE PUBLISH RESULT IN xcelEndpoint.py process_send_mqtt()")
            # logging.info("=" * 80)
            # logging.info(f"Publish result: {publish_result}")
            # logging.info("=" * 80)

    def mqtt_publish(self, topic: str, message: str, retain=False) -> int:
        """
        Publish the given message to the topic associated with the class
       
        Returns: integer
        """
        result = [0]

        #DEBUGGING: Add detailed logging before MQTT publish
        
        logging.info(
            "L333 xcelEndPoint() => mqtt_publish() => Preparing to publish message")
        logging.info(f"L334 xcelEndPoint() => mqtt_publish() at Topic: '{topic}'")
        # logging.info(f"L335 xcelEndPoint() => mqtt_publish() Topic type: {type(topic)}")
        logging.info(f"L333 xcelEndPoint() => mqtt_publish() Message: '{message}'")
        logging.info(f"L334 xcelEndPoint() => mqtt_publish() MQTT Client connected: {self.client.is_connected()}")
        logging.info("=" * 80)

        # logging.debug("THIS IS WHERE THE ACTUAL PUBLISH HAPPENS!!!!!\n\n\n")
        # logging.debug("=========================================================")

    

        # DEBUGGING: Add detailed logging right before client.publish call
        # logging.info("=" * 80)
        # logging.info(
        #     "ABOUT TO CALL MQTT CLIENT.PUBLISH IN xcelEndpoint.py mqtt_publish()")
        # logging.info("=" * 80)
        # logging.info(
        #     f"Calling: self.client.publish('{topic}', '{message}', retain={retain})")
        # logging.info("=" * 80)

        result = self.client.publish(topic, str(message), retain=retain)
        
        # logging.info(f"L357 xcelEndPoint() => mqtt_publish() Publish Result boolean : {result.is_published()}")
        # logging.info(f"L358 xcelEndPoint() => mqtt_publish() Publish Result  : {result}")
    
        # print(f"\n MQTT Send Result: \t\t{result}")
        # Return status of the published message
        return result[0]

    def run(self) -> None:
        """
        Main business loop for the endpoint class.
        Read from the meter, process and send over MQTT

        Returns: None
        """


        reading = self.get_reading()

    
        self.process_send_mqtt(reading)

    
