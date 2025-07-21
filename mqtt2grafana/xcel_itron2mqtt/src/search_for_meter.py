from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from typing import Tuple, Optional
from time import sleep
from xcelMeter import xcelMeter
from XcelListener import Listener


def mDNS_search_for_meter() -> Tuple[str, int]:
    """
    Creates a new zeroconf instance to probe the network for the meter
    to extract its ip address and port. Closes the instance down when complete.

    searches for the meter over the wifi network using mDNS and retruns ip address and port

    Returns: tuple of (ip_address, port) of the meter
    """
    zeroconf = Zeroconf()
    listener = Listener()
    # Meter will respond on _smartenergy._tcp.local. port 5353
    browser = ServiceBrowser(zeroconf, "_smartenergy._tcp.local.", listener)
    # Have to wait to hear back from the asynchrounous listener/browser task
    sleep(10)

    if listener.info is None:
        zeroconf.close()
        raise TimeoutError('Waiting too long to get response from meter')

    try:
        addresses = listener.info.addresses
        print(listener.info)
        # Auto parses the network byte format into a legible address
        ip_address = listener.info.parsed_addresses()[0]
        port = listener.info.port
        if port is None:
            raise ValueError('Meter port is None')
    except (AttributeError, IndexError, ValueError) as e:
        zeroconf.close()
        raise TimeoutError(f'Invalid response from meter: {e}')

    # Close out our mDNS discovery device
    zeroconf.close()
  
    return ip_address, port