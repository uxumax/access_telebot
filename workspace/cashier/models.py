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


class CryptoInvoiceStatusChoice(models.TextChoices):
    PAYING = "PAYING", "PAYING"
    PAID = "PAID", "PAID"
    CONFIRMED = "CONFIRMED", "CONFIRMED"
    REDEEMED = "REDEEMED", "REDEEMED"
    CANCELED = "CANCELED", "CANCELED"
    EXPIRED = "EXPIRED", "EXPIRED"
    

class CryptoCurrencyChoices(models.TextChoices):
    USDT = "USDT", "USDT"
    BTC = "BTC", "BTC"


class CryptoNetworkChoices(models.TextChoices):
    TRON = "TRON", "TRON (TRC20)"
    BTC = "BTC", "BTC"


class TronAddressStatusChoices(models.TextChoices):
    FREE = "FREE", "FREE"
    BUSY = "BUSY", "BUSY"


class CurrencyTypeChoices(models.TextChoices):
    FIAT = "FIAT", "FIAT"
    CRYPTO = "CRYPTO", "CRYPTO"


class InvoiceConfirmCheckerWorkerStat(main.models.WorkerStatAbstract):
    """Worker stat model"""


class InvoiceExpireCheckerWorkerStat(main.models.WorkerStatAbstract):
    """Worker stat model"""


class TronTransactionCheckerWorkerStat(main.models.WorkerStatAbstract):
    """Worker stat model"""


class TempModelAbstract(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BuildingInvoice(TempModelAbstract):
    BUILDING_TIMEOUT = timedelta(minutes=30)

    customer = models.OneToOneField(
        main.models.Customer, 
        on_delete=models.CASCADE,
        related_name="building_invoice"
    )
    subscription = models.ForeignKey(
        accesser.models.Subscription, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True
    )
    duration = models.ForeignKey(
        accesser.models.SubscriptionDurationPrice,
        on_delete=models.CASCADE, 
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=19, 
        decimal_places=6,
        null=True,
        blank=True
    )
    network = models.CharField(
        max_length=100,
        choices=CryptoNetworkChoices.choices,
        null=True,
        blank=True
    )
    currency = models.CharField(
        max_length=10,
        choices=CryptoCurrencyChoices.choices,
        null=True,
        blank=True
    )
    currency_type = models.CharField(
        max_length=6,
        choices=CurrencyTypeChoices.choices,
        null=True,
        blank=True
    )
    expire_date = models.DateTimeField()

    # def has_one_duration_only(self):
    #     return self.subscription.durations.count() == 1

    def save(self, *args, **kwargs):
        from . import signals
        if self.pk is None:  # is creating
            signals.BuildingInvoicePreCreate(self)
        super().save(*args, **kwargs)


class CryptoInvoice(models.Model):
    PAYING_TIMEOUT = timedelta(minutes=60)
    
    customer = models.ForeignKey(
        main.models.Customer, 
        on_delete=models.CASCADE,
        related_name="crypto_invoices"
    )
    subscription = models.ForeignKey(
        accesser.models.Subscription, 
        on_delete=models.SET_NULL,
        null=True
    )
    duration = models.ForeignKey(
        accesser.models.SubscriptionDurationPrice,
        on_delete=models.CASCADE, 
        null=True
    )
    address = models.CharField(
        max_length=128,        
    )
    status = models.CharField(
        max_length=20,
        choices=CryptoInvoiceStatusChoice.choices,
        default=CryptoInvoiceStatusChoice.PAYING
    )
    network = models.CharField(
        max_length=100,
        choices=CryptoNetworkChoices.choices,
    )
    amount = models.DecimalField(
        max_digits=19, 
        decimal_places=6
    )
    currency = models.CharField(
        max_length=10,
        choices=CryptoCurrencyChoices.choices,
    )
    expire_date = models.DateTimeField()

    create_date = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"cInvoice({self.id}:{self.customer.id}:{self.status})"

    def confirmed(self):
        from . import signals
        signals.CryptoInvoiceConfirmed(self)
        self.save()

    def canceled(self):
        from . import signals
        signals.CryptoInvoiceCanceled(self)
        self.save()

    def expired(self):
        from . import signals
        signals.CryptoInvoiceExpired(self)
        self.save()

    def save(self, *args, **kwargs):
        from . import signals
        if self.pk is None:  # is creating
            signals.CryptoInvoicePreCreate(self)
        super().save(*args, **kwargs)


class TronAddress(models.Model):
    status = models.CharField(
        max_length=10,
        choices=TronAddressStatusChoices.choices,
        default=TronAddressStatusChoices.FREE,
    )
    address = models.CharField(max_length=34)
    private_key = EncryptedCharField(max_length=64)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}"


class CryptoTransaction(models.Model):
    invoice = models.ForeignKey(
        CryptoInvoice,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    txid = models.CharField(max_length=100)
    current_confirmations = models.IntegerField(default=0)
    required_confirmations = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_confirmed(self):
        return self.current_confirmations >= self.required_confirmations
