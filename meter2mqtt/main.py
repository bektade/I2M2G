import os
import logging
from xcelMeter import xcelMeter

INTEGRATION_NAME = "Xcel Itron 5 Demo"

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)

def get_meter_config() -> tuple:
    """
    Get meter configuration from environment variables
    
    Returns: tuple of (ip_address, port, creds) for meter
    """
    # Check if we're using real meter or simulator
    meter_ip = os.environ.get('METER_IP')
    meter_port = os.environ.get('METER_PORT')
    
    if meter_ip and meter_port:
        # Real meter configuration
        ip_address = meter_ip
        port = int(meter_port)
        cert_path = os.environ.get('CERT_PATH')
        key_path = os.environ.get('KEY_PATH')
        
        # Adjust certificate paths for local development
        if not os.environ.get('DOCKER_ENV'):
            if cert_path and cert_path.startswith('/opt/meter2mqtt/'):
                cert_path = cert_path.replace('/opt/meter2mqtt/', './')
            if key_path and key_path.startswith('/opt/meter2mqtt/'):
                key_path = key_path.replace('/opt/meter2mqtt/', './')
        
        creds = None
        if cert_path and key_path:
            creds = (cert_path, key_path)
        
        print(f"Configuration:")
        print(f"  Real Meter: {ip_address}:{port}")
        print(f"  Certificates: {'Yes' if creds else 'No'}")
        if creds:
            print(f"  Certificate Path: {cert_path}")
            print(f"  Key Path: {key_path}")
        print(f"  MQTT Server: {os.environ.get('MQTT_SERVER', 'mqtt')}:{os.environ.get('MQTT_PORT', '1883')}")
        
        return ip_address, port, creds
    else:
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
    # Get meter configuration (works for both Docker and local)
    ip_address, port_num, creds = get_meter_config()
    
    # Create meter instance
    meter = xcelMeter(INTEGRATION_NAME, ip_address, port_num, creds)
    meter.setup()

    if meter.initalized:
        print("Meter initialized successfully. Starting polling loop...")
        # The run method controls all the looping, querying, and mqtt sending
        meter.run()
    else:
        print("Failed to initialize meter")

        