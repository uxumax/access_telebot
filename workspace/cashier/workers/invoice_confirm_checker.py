from time import sleep
from django.utils import timezone

from main.workers import core
from access_telebot.logger import get_logger
from messenger.routers import build_callback_inline_reply
from cashier.models import (
    CryptoInvoice,
)

log = get_logger(__name__)


class Worker(core.Worker):
    def start(self, interval=60 * 1):
        while not self.stop_event.is_set():
            self._beat()
            self.stop_event.wait(interval)

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


