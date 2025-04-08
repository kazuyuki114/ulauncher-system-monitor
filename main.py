import time
from tkinter.tix import ROW
import logging
import psutil
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

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

        # Fetch system metrics using psutil
        cpu = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
        # Optionally, gather uptime info (e.g., from psutil.boot_time())
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

        logger.info("System metrics extracted")

        # Create list items for Ulauncher to show
        items = []
        items.append(ExtensionResultItem(
            icon='images/cpu.png',
            name=f"CPU: {cpu}%",
            description=f"Current CPU usage",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/ram.png',
            name=f"Memory: {memory.percent}%",
            description=f"Used: {self._bytes_to_gb(memory.used)} / Total: {self._bytes_to_gb(memory.total)}",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/disk.png',
            name=f"Disk: {disk.percent}%",
            description=f"Used: {self._bytes_to_gb(disk.used)} / Total: {self._bytes_to_gb(disk.total)}",
            on_enter=HideWindowAction()
        ))
        if battery:
            # Determine power mode based on battery.power_plugged boolean
            mode = "Plugged In" if battery.power_plugged else "On Battery"

            # Check if secsleft is -1; if so, display "N/A", otherwise convert
            time_left = "N/A" if battery.secsleft == -1 else self._secs_to_hours(battery.secsleft)

            items.append(ExtensionResultItem(
                icon='images/battery.png',
                name=f"Battery: {round(battery.percent, 2)}%({mode}) | Time left: {time_left}",
                description="Battery status",
                on_enter=HideWindowAction()
            ))

        items.append(ExtensionResultItem(
            icon='images/network.png',
            name=f"Network: Sent {self._bytes_to_gb(round(net.bytes_sent, 2))}, Received {self._bytes_to_gb(round(net.bytes_recv, 2))}",
            description="Network activity",
            on_enter=HideWindowAction()
        ))
        items.append(ExtensionResultItem(
            icon='images/uptime.png',
            name=f"Uptime: {uptime_str}",
            description="System uptime",
            on_enter=HideWindowAction()
        ))
        return RenderResultListAction(items)

    def _bytes_to_gb(self, num_bytes):
        gb = num_bytes / (1024 * 1024 * 1024)
        return f"{gb:.1f} GB"

    def _secs_to_hours(secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

class PreferencesEventListener(EventListener):
	def on_event(self, event, extension):
		extension.keyword = event.preferences["recents_kw"]


class PreferencesUpdateEventListener(EventListener):
	def on_event(self, event, extension):
		if event.id == "recents_kw":
			extension.keyword = event.new_value

if __name__ == '__main__':
    SystemMonitorExtension().run()
