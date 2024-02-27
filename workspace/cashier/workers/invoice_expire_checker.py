from time import sleep
from django.utils import timezone

from access_telebot.logger import get_logger
from cashier.models import (
    BuildingInvoice,
    CryptoInvoice,
)

log = get_logger(__name__)


class InvoiceExpireCheckWorker:
    def start_loop(self, interval=60 * 1):
        while True:
            self._delete_expired_building_invoices()
            self._set_expired_paying_crypto_invoices()
            sleep(interval)

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


def start():
    InvoiceExpireCheckWorker().start_loop()