from django.core.management.base import BaseCommand, CommandError
from threading import Thread
import signal
import sys

from main.workers import (
    webhook_tunneler,
)
from cashier.workers import (
    tron_transaction_checker,
    invoice_expire_checker,
    invoice_confirm_checker,
)
from accesser.workers import (
    customer_access_revoker,
)


class Command(BaseCommand):
    help = 'Run all workers in several threads'

    def sigint_handler(self, signal, frame):
        self.stdout.write(
            self.style.WARNING(
                'Interrupt signal received. Shutting down...'
            )
        )
        for worker in self.workers:
            worker.stop()
        for thread in self.threads:
            thread.join()

    def handle(self, *args, **options):
        self.workers = [
            webhook_tunneler.Worker(),
            tron_transaction_checker.Worker(),
            invoice_expire_checker.Worker(),
            invoice_confirm_checker.Worker(),
            customer_access_revoker.Worker(),
        ]
        self.threads = []

        signal.signal(signal.SIGINT, self.sigint_handler)

        for worker in self.workers:
            print("Worker", worker, "started")
            thread = Thread(
                target=worker.start
            )
            thread.start()
            self.threads.append(thread)

        self.stdout.write(
            self.style.SUCCESS(
                'All workers have been started. Use Ctrl+C to stop.'
            )
        )

        for thread in self.threads:
            thread.join()

        self.stdout.write(
            self.style.SUCCESS(
                'All workers have been stopped.'
            )
        )
