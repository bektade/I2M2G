# mDNS listener to find the IP Address of the meter on the network
from zeroconf import ServiceListener, Zeroconf


class Listener(ServiceListener):
    def __init__(self):
        self.info = None

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self.info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {self.info}")