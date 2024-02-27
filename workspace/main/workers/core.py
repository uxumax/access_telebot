from threading import Event


class Worker:
    def __init__(self):
        self.stop_event = Event()

    # Example; have to overwrite this method
    def start_loop(self, interval=60):
        while not self.stop_event.is_set():
            self.stop_event.wait(interval)

    def stop(self):
        self.stop_event.set()


