import os
import logging
from xcelMeter import xcelMeter

INTEGRATION_NAME = "Xcel Itron 5 Demo"

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)

def get_meter_simulator_config() -> tuple:
    """
    Get meter simulator configuration from environment variables
    
    Returns: tuple of (ip_address, port, creds) for meter
    """
 
    # Simulator configuration
    ip_address = os.environ.get('SIMULATOR_IP', 'localhost')
    port = int(os.environ.get('SIMULATOR_PORT', '8082'))
    
    # Determine MQTT server for display
    mqtt_server = os.environ.get('MQTT_SERVER', 'localhost')
    if mqtt_server == 'mqtt' and not os.environ.get('DOCKER_ENV'):
        mqtt_server = 'localhost'
    
    print(f"Configuration:")
    print(f"  Simulator: {ip_address}:{port}")
    print(f"  MQTT Server: {mqtt_server}:{os.environ.get('MQTT_PORT', '1883')}")
    
    return ip_address, port, None

if __name__ == '__main__':
    # Get meter simulator configuration 
    ip_address, port_num, creds = get_meter_simulator_config()
    
    # Create meter instance
    meter = xcelMeter(INTEGRATION_NAME, ip_address, port_num, creds)
    meter.setup()

    if meter.initalized:
        print("Meter initialized successfully. Starting polling loop...")
        # The run method controls all the looping, querying, and mqtt sending
        meter.run()
    else:
        print("Failed to initialize meter")

        