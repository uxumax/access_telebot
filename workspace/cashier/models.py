from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import typing
import cashier.types
import main.models
import accesser.models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField


class TransactionStatusChoices(models.TextChoices):
    CREATED = "CREATED", "CREATED"
    PAID = "PAID", "PAID"
    FAIL = "FAIL", "FAIL"
    CANCELED = "CANCELED", "CANCELED"


class InvoiceStatusChoice(models.TextChoices):
    BUILDING = "BUILDING", "BUILDING"
    PAYING = "PAYING", "PAYING"
    PAID = "PAID", "PAID"
    CANCELED = "CANCELED", "CANCELED"


class CryptoCurrencyChoices(models.TextChoices):
    USDT = "USDT", "USDT"
    BTC = "BTC", "BTC"


class CryptoNetworkChoices(models.TextChoices):
    TRON = "TRON", "TRON (TRC20)"
    BTC = "BTC", "BTC"


class TronAddressStatusChoices(models.TextChoices):
    FREE = "FREE", "FREE"
    BUSY = "BUSY", "BUSY"


class TronAddress(models.Model):
    status = models.CharField(
        max_length=10,
        choices=TronAddressStatusChoices.choices,
        default=TronAddressStatusChoices.FREE,
    )
    address = models.CharField(max_length=34)
    private_key = EncryptedCharField(max_length=64)
    created_at_date = models.DateTimeField(auto_now_add=True)


class CryptoInvoice(models.Model):
    PAY_TIMEOUT = timedelta(minutes=60)

    customer = models.ForeignKey(
        main.models.Customer, 
        on_delete=models.CASCADE
    )
    subscription = models.ForeignKey(
        accesser.models.Subscription, 
        on_delete=models.SET_NULL, 
        null=True
    )
    address = models.ForeignKey(
        TronAddress,
        on_delete=models.PROTECT, 
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatusChoice.choices,
        default=InvoiceStatusChoice.BUILDING        
    )
    network = models.CharField(
        max_length=100,
        choices=CryptoNetworkChoices.choices,
        null=True
    )

    amount = models.DecimalField(
        max_digits=19, 
        decimal_places=6
    )
    currency = models.CharField(
        max_length=10,
        choices=CryptoCurrencyChoices.choices,
        null=True
    )
    start_building_date = models.DateTimeField(auto_now_add=True)

    expire_date = models.DateTimeField(null=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def paid(self):
        self.paid_date = timezone.now()
        self.status = TransactionStatusChoices.PAID 
        self.save()


class CryptoTransaction(models.Model):
    invoice = models.ForeignKey(
        CryptoInvoice,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    txid = models.CharField(max_length=100)
    confirmations = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


