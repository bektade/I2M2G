
import time
import sys
import paho.mqtt.client as mqtt
import os
import json
from publisher import publish_to_mqtt
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
