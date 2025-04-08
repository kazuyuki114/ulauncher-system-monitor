import os
import netifaces

class NetworkConnectionDetector:
    def __init__(self):
        """Initialize by setting the default network interface."""
        self.default_iface = self.get_default_interface()

    def get_default_interface(self):
        """
        Get the default network interface used for internet connection.
        Returns the interface name or None if not found.
        """
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default')
        if default_gateway and netifaces.AF_INET in default_gateway:
            # The default gateway tuple: (gateway_ip, interface, ...)
            return default_gateway[netifaces.AF_INET][1]
        return None

    def check_connection_type(self, interface):
        """
        Check if the given interface is wireless or ethernet.
        - On Linux, checks for the '/sys/class/net/<interface>/wireless' directory.
        - On other platforms, uses interface name heuristics.
        """
        if os.name == 'posix':
            # For Linux/Unix platforms: check for the wireless subdirectory
            wireless_path = f'/sys/class/net/{interface}/wireless'
            if os.path.isdir(wireless_path):
                return "Wi-Fi"
            else:
                return "Ethernet"
        else:
            # For other platforms (e.g., Windows), use heuristic based on interface name.
            interface_lower = interface.lower()
            if any(keyword in interface_lower for keyword in ['wlan', 'wifi', 'wireless']):
                return "Wi-Fi"
            else:
                return "Ethernet"

    def detect_connection(self):
        """
        Detect and return the default interface and its connection type.
        Returns a tuple (interface, connection_type) or (None, None) if no default interface is found.
        """
        if self.default_iface:
            conn_type = self.check_connection_type(self.default_iface)
            return self.default_iface, conn_type
        else:
            return None, None
