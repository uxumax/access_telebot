import os
import logging
from django.core.management.base import BaseCommand
from threading import (
    Thread, 
    # Timer, 
    Event
)
import signal

from main.workers import (
    webhook_tunneler,
    infinity_poller,
)
from cashier.workers import (
    tron_transaction_checker,
    invoice_expire_checker,
    invoice_confirm_checker,
)
from accesser.workers import (
    customer_access_revoker,
    chat_updater,
)
from messenger.workers import (
    periodic_notifier,
)

stop_event = Event()
logging.basicConfig(
    level=logging.ERROR, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Run all workers in several threads and monitor their last beat"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workers = [
            tron_transaction_checker.Worker(),
            invoice_expire_checker.Worker(),
            invoice_confirm_checker.Worker(),
            customer_access_revoker.Worker(),
            chat_updater.Worker(),
            periodic_notifier.Worker(),
        ]

        # Set Telegam API connection worker type 
        is_using_webhook = os.getenv("USE_TELEGRAM_API_WEBHOOK") == "true"
        if is_using_webhook:
            self.workers.append(webhook_tunneler.Worker())
        else:
            self.workers.append(infinity_poller.Worker())

        self.threads = []

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, self._sigint_handler)

        for worker in self.workers:
            print("Worker", worker, "started")
            thread = Thread(target=lambda: self.start_worker_with_error_logging(worker))
            thread.start()
            self.threads.append(thread)

        self.stdout.write(
            self.style.SUCCESS("All workers have been started. Use Ctrl+C to stop.")
        )

        stop_event.wait()  # Ожидание сигнала остановки

    def _sigint_handler(self, signum, frame):
        self.stdout.write(
            self.style.WARNING("Interrupt signal received. Shutting down...")
        )
        stop_event.set()  # Установка события остановки для остановки всех потоков

        for worker in self.workers:
            worker.stop()  # Убедитесь, что у ваших воркеров есть метод stop()

        for thread in self.threads:
            if thread.is_alive():
                thread.join()  # Ожидание завершения работы потока

        self.stdout.write(self.style.SUCCESS("All workers have been stopped."))

    def start_worker_with_error_logging(self, worker):
        try:
            worker.start()
        except Exception as e:
            logging.exception(
                f"Error in worker {type(worker).__name__}: {e}", exc_info=True
            )
