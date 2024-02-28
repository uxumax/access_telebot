from time import sleep
from django.utils import timezone

from main.workers import core
from access_telebot.logger import get_logger
from cashier.models import (
    BuildingInvoice,
    CryptoInvoice,
    InvoiceExpireCheckerWorkerStat
)

log = get_logger(__name__)


class Worker(core.Worker):
    beat_interval = 60 * 1 
    stat = InvoiceExpireCheckerWorkerStat

    def start(self):
        while not self.stop_event.is_set():
            self._beat()
            self.wait()

    def _beat(self):
        self._delete_expired_building_invoices()
        self._set_expired_paying_crypto_invoices()

    @staticmethod
    def _delete_expired_building_invoices():
        # Возвращает количество удаленных объектов и детали
        deleted_count, _ = BuildingInvoice.objects.filter(
            expire_date__lte=timezone.now()
        ).delete()
        if deleted_count > 0:
            log.info(f"Deleted {deleted_count} expired building invoices.")

    @staticmethod
    def _set_expired_paying_crypto_invoices():
        # Возвращает количество обновленных записей
        updated_count = CryptoInvoice.objects.filter(
            status="PAYING",
            expire_date__lte=timezone.now()
        ).update(
            status="EXPIRED"
        )
        if updated_count > 0:
            log.info(f"Set {updated_count} crypto invoices as expired.")


