
import time
import sys
import paho.mqtt.client as mqtt
import os
import json
from getSimulatedData import getInstantaneousMeterReading, getDeviceID


"""


main_simulated_pub.py does this:

- sends get request to EnergyLaunchpad's meterSimulator 
- gets instantaneous meter reading for a given meterReadingId and deviceID (sFDI)
- publishes the instantaneous meter reading value to MQTT broker using publisher.py


what it needs:
- specify host IP of the machhine in .env file ( helps to construct url endpoint to the meterSimulator ) e.g. http://10.195.250.49:8082/swagger/index.html
- run the mqtt2grafanna (this is the destination of the published data)

"""

import paho.mqtt.client as mqtt
import os
import logging
import yaml


"""

publisher.py


- this code pubslises readings from simulator to MQTT broker
- uses config.yml for output formatting style 

"""

# Load configuration


def load_config():
    """Load configuration from config.yml"""
    try:
        with open('config.yml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        # Default configuration if file doesn't exist
        return {
            'output_level': 'bare_minimum',
            'formats': {
                'bare_minimum': {
                    'show_connection': False,
                    'show_topic': False,
                    'show_message_id': False,
                    'show_docker_info': False,
                    'show_success_only': True,
                    'emoji': False,
                    'minimal_logging': True
                }
            }
        }


# Load config
config = load_config()
output_config = config['formats'].get(
    config['output_level'], config['formats']['bare_minimum'])

# Set up logging based on config
if output_config.get('minimal_logging', False):
    # Minimal logging - only show errors
    logging.basicConfig(level=logging.ERROR, format='%(message)s')
else:
    # Normal logging
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if not output_config['show_connection']:
        return

    if rc == 0:
        status = "✅ Connected to MQTT broker" if output_config[
            'emoji'] else "Connected to MQTT broker"
        logger.info(status)
    else:
        status = f"❌ MQTT connection failed (code: {rc})" if output_config[
            'emoji'] else f"MQTT connection failed (code: {rc})"
        logger.error(status)


def on_publish(client, userdata, mid):
    """Callback for when a message is published"""
    if output_config['show_message_id']:
        status = f"✅ Message published (ID: {mid})" if output_config[
            'emoji'] else f"Message published (ID: {mid})"
    else:
        status = "✅ Message published" if output_config['emoji'] else "Message published"
    logger.info(status)


def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the broker"""
    if rc != 0 and not output_config['show_success_only']:
        status = f"⚠️ MQTT disconnected (code: {rc})" if output_config[
            'emoji'] else f"MQTT disconnected (code: {rc})"
        logger.warning(status)


def publish_to_mqtt(value, sFDI):
    """Publish only the value to MQTT topic"""
    try:
        # Create MQTT client
        client = mqtt.Client()

        # Set up callbacks
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.on_disconnect = on_disconnect

        # Get MQTT configuration from environment
        # Check if we're running in a container or locally
        if os.path.exists('/.dockerenv'):
            # Running inside Docker container
            mqtt_host = os.getenv('MQTT_SERVER', 'xcel_itron2mqtt')
        else:
            # Running locally - connect to Mosquitto container on localhost
            mqtt_host = os.getenv('MQTT_SERVER', 'localhost')

        mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        topic_prefix = os.getenv('MQTT_METER_TOPIC_PREFIX', 'xcel_itron_5')

        # Show Docker info if configured
        if output_config['show_docker_info']:
            env_info = "inside Docker" if os.path.exists(
                '/.dockerenv') else "locally"
            logger.info(f"🌐 Running {env_info}")

        # Connect to MQTT broker
        client.connect(mqtt_host, mqtt_port, 60)

        # Start the network loop to handle callbacks
        client.loop_start()

        # Construct topic
        topic = "xcel_itron5/sFDI/Power_Demand/state"
        message = str(value)

        # Show publishing info based on config
        if output_config['show_topic']:
            publish_msg = f"📤 Publishing {message} to {topic}" if output_config[
                'emoji'] else f"Publishing {message} to {topic}"
            logger.info(publish_msg)
        elif not output_config.get('minimal_logging', False):
            publish_msg = f"📤 Publishing {message}" if output_config[
                'emoji'] else f"Publishing {message}"
            logger.info(publish_msg)

        logger.info(f"Publishing to topic: {topic} with message: {message}")
        print(f"Publishing to topic: {topic} with message: {message}")

        # Publish message
        result = client.publish(topic, message)

        # Wait a moment for the publish callback to be called
        import time
        time.sleep(0.1)

        # Check if publish was successful and show minimal output
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            if output_config.get('minimal_logging', False):
                # In minimal mode, show message and success status
                print(f"Published: {message} ✓")
                print()  # Add two new lines for spacing
            else:
                # Normal mode - use logging
                status = "✅ Message published" if output_config['emoji'] else "Message published"
                logger.info(status)
                print()  # Add two new lines for spacing
                print()
        else:
            error_msg = f"❌ Publish failed (error code: {result.rc})" if output_config[
                'emoji'] else f"Publish failed (error code: {result.rc})"
            logger.error(error_msg)
            print()  # Add two new lines for spacing even on error
            print()

        # Stop the network loop and disconnect
        client.loop_stop()
        client.disconnect()

    except Exception as e:
        error_msg = f"❌ MQTT error: {str(e)}" if output_config['emoji'] else f"MQTT error: {str(e)}"
        logger.error(error_msg)
        # Don't raise the exception - just log it and continue


# Main execution
if __name__ == "__main__":
    # Get meterReadingId from command line argument, default to 1
    meter_reading_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    host_ip = os.getenv('HOST_IP', 'localhost')

    print(f"Meter Agent Simulator")
    print(f"Monitoring meterReadingID: {meter_reading_id}")
    print(f"Connecting to simulator at: {host_ip}:8082")
    print("")

    while True:
        try:
            value, touTier = getInstantaneousMeterReading(meter_reading_id)
            sFDI = getDeviceID()

            # Publish only the value to MQTT
            publish_to_mqtt(value, sFDI)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(5)  # Publish every 5 seconds
