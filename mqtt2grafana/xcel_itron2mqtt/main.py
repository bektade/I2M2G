import os
import logging
from pathlib import Path
from xcelMeter import xcelMeter   # to cretae a meter object using xcelMeter Class
from src.search_for_meter import mDNS_search_for_meter
from src.auth.verifyCred import look_for_creds


INTEGRATION_NAME = "Xcel Itron 5"
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)


if __name__ == '__main__':
    # Get meter IP and port from environment or use mDNS discovery

    """
    step-1: Get Meter IP & Port
    
    if the meter IP is found in .env file get it from there, 
    otherswise look for it using mDNS discovery
    """
    meter_ip = os.getenv('METER_IP')
    meter_port = os.getenv('METER_PORT')

    if meter_ip and meter_port:
        ip_address = meter_ip
        port_num = int(meter_port)
    else:
        ip_address, port_num = mDNS_search_for_meter()

    """
    step-2: Get Credentials 
    """
    creds = look_for_creds()

    """
    step-3: create a meter object 

    use creds + ip + port to initialize the meter
    """
    myFirstMeter = xcelMeter(INTEGRATION_NAME, ip_address, port_num, creds)
    myFirstMeter.setup()

    if myFirstMeter.initalized:
        # The run method controls all the looping, querying, and mqtt sending
        myFirstMeter.run()
