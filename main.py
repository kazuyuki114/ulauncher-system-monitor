import time
from tkinter.tix import ROW
import logging
import psutil
from NetworkConnectionDetector import NetworkConnectionDetector
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from jedi.api.classes import Name

logger = logging.getLogger(__name__)

class SystemMonitorExtension(Extension):
    def __init__(self):
        super(SystemMonitorExtension, self).__init__()
        # Subscribe to the keyword query event
        self.subscribe(KeywordQueryEvent, SystemMonitorEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesEventListener())

class SystemMonitorEventListener(EventListener):
    def on_event(self, event, extension):

        logger.info("Start extracting system metrics")

        # CPU metrics
        cpu = psutil.cpu_percent(interval=1.0)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_stat = psutil.cpu_freq()

        # Memory metrics
        memory = psutil.virtual_memory()

        # Disk metrics
        disk = psutil.disk_usage('/')

        # Network metrics
        network_metrics = self._get_network_metrics(interval=1.0)
        detector = NetworkConnectionDetector()
        iface, conn_type = detector.detect_connection()

        # Battery metrics
        battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

        # Uptime
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

        logger.info("System metrics extracted")

        # Create list items for Ulauncher to show
        items = []
        items.append(ExtensionResultItem(
            icon='images/cpu.png',
            name=f"CPU: {cpu}% / Cores: {cpu_count}",
            description=f"Current:{round(cpu_stat.current,2)}MHz/Min:{round(cpu_stat.min,2)} MHz/Max:{round(cpu_stat.max,2)}MHz",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/ram.png',
            name=f"Memory: {memory.percent}%",
            description=f"Used: {self._bytes_to_readable(memory.used)}GB / Total: {self._bytes_to_readable(memory.total)}GB",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/disk.png',
            name=f"Disk: {disk.percent}%",
            description=f"Used: {self._bytes_to_readable(disk.used)}GB / Total: {self._bytes_to_readable(disk.total)}GB",
            on_enter=HideWindowAction()
        ))
        if battery:
            # Check if secsleft is -1; if so, display "N/A", otherwise convert
            time_left = "N/A" if battery.secsleft == -1 else self._secs_to_hours(battery.secsleft)
            items.append(ExtensionResultItem(
                icon='images/battery.png',
                name="Battery Status",
                description=f"Battery:{round(battery.percent, 2)}%| Time left: {time_left}",
                on_enter=HideWindowAction()
            ))

        items.append(ExtensionResultItem(
            icon='images/network.png',
            name=f"Network: {conn_type}",
            description = f"Down:{self._bytes_to_readable(network_metrics['download_speed'])}/s|Up:{self._bytes_to_readable(network_metrics['upload_speed'])}/s",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/uptime.png',
            name=f"Uptime: {uptime_str}",
            description="System uptime",
            on_enter=HideWindowAction()
        ))
        return RenderResultListAction(items)

    def _bytes_to_readable(self,num_bytes):
        """Convert bytes to a human-readable format."""
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if num_bytes < 1024:
                return f"{num_bytes:.2f} {unit}"
            num_bytes /= 1024
        return f"{num_bytes:.2f} TB"

    def _secs_to_hours(self, secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def _get_network_metrics(self, interval=1.0):
        # Get initial counters
        net1 = psutil.net_io_counters()
        time.sleep(interval)
        net2 = psutil.net_io_counters()

        # Calculate speeds
        bytes_sent = net2.bytes_sent - net1.bytes_sent
        bytes_recv = net2.bytes_recv - net1.bytes_recv

        upload_speed = bytes_sent / interval  # bytes/sec
        download_speed = bytes_recv / interval  # bytes/sec

        # Total traffic (since boot)
        total_sent = net2.bytes_sent
        total_recv = net2.bytes_recv

        return {
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "total_downloaded": total_recv,
            "total_uploaded": total_sent
        }

class PreferencesEventListener(EventListener):
	def on_event(self, event, extension):
		extension.keyword = event.preferences["recents_kw"]


class PreferencesUpdateEventListener(EventListener):
	def on_event(self, event, extension):
		if event.id == "recents_kw":
			extension.keyword = event.new_value

if __name__ == '__main__':
    SystemMonitorExtension().run()
