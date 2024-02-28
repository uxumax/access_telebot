from threading import Event
from django.utils import timezone


class Worker:
    def __init__(self):
        self.stop_event = Event()

    # Example; have to overwrite this method
    def start_loop(self, interval=60):
        while not self.stop_event.is_set():
            self.wait()

    def wait(self):
        self._update_last_beat_date()
        self.stop_event.wait(self.beat_interval)

    def _update_last_beat_date(self):
        stat = self.stat.load()
        stat.last_beat_date = timezone.now()
        stat.save()

    def stop(self):
        self.stop_event.set()


