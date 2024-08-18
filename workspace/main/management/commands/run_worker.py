from django.core.management.base import BaseCommand, CommandError
from importlib import import_module
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
    chat_updater,
)


class Command(BaseCommand):
    help = 'Run worker in this thread'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name', 
            type=str, 
            help='App name for run'
        )
        parser.add_argument(
            'worker_filename_py', 
            type=str, 
            help='Worker filename for run'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        worker_filename = options['worker_filename_py']

        try:
            workers_module = import_module(f"{app_name}.workers")
        except ImportError:
            raise CommandError(f'Module "workers" not found in application "{app_name}".')

        worker = getattr(workers_module, worker_filename, None)
        if worker is None:
            raise CommandError(
                f'Worker filename "{worker_filename}" not found in application "{app_name}".'
            )

        worker.Worker().start()
