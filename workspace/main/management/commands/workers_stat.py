from threading import Thread, Timer, Event
import sys
from django.core.management.base import BaseCommand
from main.models import (
    WebhookTunnelerWorkerStat,
)
from cashier.models import (
    InvoiceConfirmCheckerWorkerStat,
    InvoiceExpireCheckerWorkerStat,
    TronTransactionCheckerWorkerStat,
)
from accesser.models import (
    CustomerAccessRevokerWorkerStat,
)


stop_event = Event()


class Command(BaseCommand):
    help = 'Run all workers in several threads and monitor their last beat'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workers_stat = [
            WebhookTunnelerWorkerStat,
            InvoiceConfirmCheckerWorkerStat,
            InvoiceExpireCheckerWorkerStat,
            TronTransactionCheckerWorkerStat,
            CustomerAccessRevokerWorkerStat,
        ]
        self.threads = []

    def handle(self, *args, **options):
        # Запуск потока мониторинга
        monitor_thread = Thread(
            target=self._print_worker_beats
        )
        monitor_thread.start()
        self.threads.append(monitor_thread)

    def _clear_console(self):
        """Очищает консольный вывод."""
        sys.stdout.write('\x1b[2J\x1b[H')

    def _fetch_last_beat_dates(self):
        result = []
        for worker_stat in self.workers_stat:
            stat = worker_stat.load()
            last_beat = stat.last_beat_date.strftime(
                '%Y-%m-%d %H:%M:%S'
            ) if stat else 'Never'
            result.append(
                f"{worker_stat.__name__}.last_beat_date: {last_beat}"
            )
        return result

    def _print_worker_beats(self):
        interval = 5
        try:
            while not stop_event.is_set():
                self._clear_console()
                for line in self._fetch_last_beat_dates():
                    print(line)
                stop_event.wait(interval)
        except KeyboardInterrupt:
            print("Monitoring stopped.")

