import psutil
import platform
import time
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

class SystemMonitorExtension(Extension):
    def __init__(self):
        super(SystemMonitorExtension, self).__init__()
        # Subscribe to the keyword query event
        self.subscribe(KeywordQueryEvent, SystemMonitorEventListener())

class SystemMonitorEventListener(EventListener):
    def on_event(self, event, extension):
        # Fetch system metrics using psutil
        cpu = psutil.cpu_percent(interval=1.0)  # CPU percentage, using a small delay to get a reading
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

        # Create list items for Ulauncher to show
        items = []
        items.append(ExtensionResultItem(
            icon='images/cpu.png',
            name=f"CPU: {cpu}%",
            description=f"Current CPU usage",
        ))
        items.append(ExtensionResultItem(
            icon='images/ram.png',
            name=f"Memory: {memory.percent}%",
            description=f"Used: {self._bytes_to_mb(memory.used)} / Total: {self._bytes_to_mb(memory.total)}",
        ))
        items.append(ExtensionResultItem(
            icon='images/disk.png',
            name=f"Disk: {disk.percent}%",
            description=f"Used: {self._bytes_to_mb(disk.used)} / Total: {self._bytes_to_mb(disk.total)}",
        ))
        if battery:
            items.append(ExtensionResultItem(
                icon='images/battery.png',
                name=f"Battery: {battery.percent}%",
                description="Battery status",
            ))

        # You could also add a network info item if desired
        items.append(ExtensionResultItem(
            icon='images/network.png',
            name=f"Network: Sent {self._bytes_to_mb(net.bytes_sent)}, Received {self._bytes_to_mb(net.bytes_recv)}",
            description="Network activity",
        ))

        return RenderResultListAction(items)

    def _bytes_to_mb(self, num_bytes):
        mb = num_bytes / (1024 * 1024)
        return f"{mb:.1f} MB"

if __name__ == '__main__':
    SystemMonitorExtension().run()
