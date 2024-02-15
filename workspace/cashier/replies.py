import typing
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
import telebot

from messenger.types import CallbackInlineReplyBuilderBase
import main.models
import accesser.models
import cashier.models
from . import models

from wallets.crypto import tron as tron_wallet

bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


CallbackInlineReply = typing.Union[
    'InlineReplyBuildCryptoInvoice',
]


class InlineReplyBuildCryptoInvoice(CallbackInlineReplyBuilderBase):
    building_invoice: cashier.models.CryptoInvoice = None 

    def build(self):
        self._set_data()

        if self.building_invoice is None:
            return self._start_building_new_invoice()
        else:
            return self._continue_building_invoice()

    def _set_data(self):
        self.building_invoice = models.cashier.CryptoInvoice.objects.filter(
            customer=self.customer,
            status=models.cashier.InvoiceStatusChoice.BUILDING
        ).first()

    def _start_building_new_invoice(self):
        pass

    def _continue_building_invoice(self):
        inv = self.building_invoice
        if inv.network is None and inv.currency is None:
            'choose network reply'
        if inv.address is None:
            'invoice almost ready. Only get address remain'
            'after got address timeout start and customer have to pay'
        pass


