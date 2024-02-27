from time import sleep
from django.utils import timezone

from access_telebot.logger import get_logger
from messenger.routers import build_callback_inline_reply
from cashier.models import (
    CryptoInvoice,
)

log = get_logger(__name__)


class InvoiceConfirmCheckWorker:
    def start_loop(self, interval=60 * 1):
        while True:
            self._beat()
            sleep(interval)

    def _beat(self):
        for invoice in self._get_confirmed_crypto_invoices():
            self._build_give_invite_keys_reply(invoice)

    @staticmethod
    def _get_confirmed_crypto_invoices():
        return CryptoInvoice.objects.filter(
            status="CONFIRMED"
        ).all()
    
    @staticmethod
    def _build_give_invite_keys_reply(invoice):
        return build_callback_inline_reply(
            customer=invoice.customer,
            app_name="accesser",
            reply_name="GiveInviteLinksReply",
            args=["c", invoice.id]
        )  


def start():
    InvoiceConfirmCheckWorker().start_loop()
