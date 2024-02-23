from django.db.models.signals import (
    # pre_save,
    post_save,
)
from django.dispatch import receiver
from django.utils import timezone
from access_telebot.logger import get_logger


from . import wallets
from . import models


class CryptoInvoicePreCreate:
    log = get_logger(__name__)

    def __init__(self, instance: models.CryptoInvoice):
        i = instance
        i.address = self._get_address(i.network)
        i.expire_date = self._get_expire_date()
        i.customer.building_invoice.delete()

    def _get_address(self, network: str):
        address_model = self._get_address_model(network)
        address_model.status = "BUSY"
        address_model.save()
        return address_model.address

    def _get_address_model(self, network: str):
        if network == "TRON":
            return wallets.crypto.tron.get_free_address_model()
        raise ValueError(
            f"Cannot find wallet model for network {network}"
        )
    def _get_expire_date(self):
        return timezone.now() + models.CryptoInvoice.PAYING_TIMEOUT
        

class CryptoInvoiceFinal:

    @staticmethod
    def free_address(address):
        models.TronAddress.objects.filter(
            address=address
        ).update(
            status="FREE"
        )    


class CryptoInvoiceConfirmed(CryptoInvoiceFinal):
    def __init__(self, instance: models.CryptoInvoice):
        i = instance
        i.confirmed_date = timezone.now()
        i.status = "CONFIRMED" 
        self.free_address(instance.address)


class CryptoInvoiceCanceled(CryptoInvoiceFinal):
    def __init__(self, instance: models.CryptoInvoice):
        instance.status = "CANCELED"
        self.free_address()


class CryptoInvoiceExpired(CryptoInvoiceFinal):
    def __init__(self, instance: models.CryptoInvoice):
        instance.status = "EXPIRED"
        self.free_address()

