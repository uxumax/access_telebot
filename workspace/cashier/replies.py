import typing
from django.conf import settings
from access_telebot.logger import get_logger
from telebot import TeleBot
from messenger.replies import (
    Callback,
    CallbackInlineReplyBuilder,
)
from . import wallets
import main.models
import accesser.models
import cashier.models
from . import models

from .wallets.crypto import tron as tron_wallet

bot = TeleBot(settings.TELEBOT_KEY)
log = get_logger(__name__)


CallbackInlineReply = typing.Union[
    "ChoosePayMethodReply",
    "BuildingCryptoInvoiceReply",
]


class BuildingInvoiceReplyBuilder(CallbackInlineReplyBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self._has_building_invoice():
            self.invoice = self.customer.building_invoice
        else:
            self.invoice = models.BuildingInvoice.objects.create(
                customer=self.customer
            )

    def _has_building_invoice(self):
        return hasattr(self.customer, "building_invoice")\
            and self.customer.building_invoice is not None


class ChooseAccessDurationReply(BuildingInvoiceReplyBuilder):
    USING_ARGS = (
        "subscription_id",
    )

    def build(self):
        subscription = accesser.models.Subscription.objects.get(
            pk=self._get_subscription_id()
        )
        self._update_invoice(subscription)

        if self._is_only_one_duration():
            duration = subscription.durations.first()
            return self.router.redirect(
                "ChoosePayMethodReply",
                args=duration.id
            )

        text = (
            f"Choose access period for subscription {subscription.name}"
        )
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )  

    def _get_subscription_id(self):
        return int(self.callback.args[0])

    def _update_invoice(self, subscription):
        self.invoice.subscription = subscription
        self.invoice.save()

    def _is_only_one_duration(self):
        return self.invoice.subscription.durations.count() == 1
    
    def _build_markup(self):
        durations = self.subscription.durations.all()
        for duration in durations:
            self.add_button(
                f"{duration.duration} days - {duration.price} USDT", 
                # app_name="cashier",
                reply_name="ChoosePayMethodReply",
                args=duration.id
            )

        return self.markup    


class ChoosePayMethodReply(BuildingInvoiceReplyBuilder):
    USING_ARGS = (
        'duration_id'
    )
    PAY_METHODS = (
        ("usdt_trc20", "USDT TRC20"),
    )

    def build(self):
        duration = self._get_duration_model()
        self._update_invoice(duration)

        text = (
            f"Amount for pay {duration.price} USD. Choose payment method"
        )
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )  

    def _update_invoice(
        self, 
        duration: accesser.models.SubscriptionDurationPrice
    ):
        self.invoice.duration = duration
        self.invoice.amount = duration.price
        self.invoice.save()

    def _get_duration_model(self):
        return accesser.models.SubscriptionDurationPrice.objects\
            .get(
                pk=self._get_duration_id()
            )

    def _get_duration_id(self):
        return self.callback.args[0]

    def _build_markup(self):
        for slug, caption in self.PAY_METHODS:
            self.add_button(
                caption, 
                reply_name="CheckoutReply",
                args=slug
            )

        self.add_button(
            "Back",
            reply_name="ChooseAccessDurationReply",
            args=self.invoice.subscription.id           
        )
        return self.markup


class CheckoutReply(BuildingInvoiceReplyBuilder):
    USING_ARGS = (
        "pay_method",
    )

    def build(self):
        self._update_invoice()
        text = self._get_invoice_text()
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )

    def _update_invoice(self):
        pay_method: str = self._get_pay_method()
        if pay_method == "usdt_trc20":
            self.invoice.currency_type = "CRYPTO"
            self.invoice.currency = "USDT"
            self.invoice.network = "TRON"
            self.invoice.save()
            return
        raise ValueError(
            f"Unsupported pay_method {pay_method}"
        )

    def _get_pay_method(self):
        return self.callback.args[0]

    def _get_invoice_text(self):
        i = self.invoice
        text = (
            "Check you summary invoice data\n"
            f"Subscription: {i.subscription.name}\n"
            f"Duration: {i.duration.duration}\n"
        )

        if i.currency_type == "CRYPTO":
            text += (
                f"Amount: {i.amount} {i.currency}\n"
                f"Network: {i.network}\n"
            )
            
        return text 

    def _build_markup(self):
        if self.invoice.currency_type == "CRYPTO":
            self.add_button(
                "Pay",
                reply_name="CryptoPayingReply"
            )
        elif self.invoice.currency_type == "FIAT":
            pass
        else:
            raise ValueError(
                "Unsupported invoice currency type"
            )
        self.add_button(
            "Back",
            reply_name="ChoosePayMethodReply",
            args=self.invoice.duration.id           
        )
        return self.markup


class CryptoPayingReply(BuildingInvoiceReplyBuilder):

    def build(self):
        invoice = self._deploy_invoice()
        self.send_message(
            (
                f"We have been reserved for you {invoice.network} address "
                f"for {invoice.PAYING_TIMEOUT} minutes. "
                f"Please send funds during this time."
            )
        )
        self.send_message(
            (
                f"Please send {invoice.currency} to this address "
                "and exactly this amount:"
            ),
        )
        self.send_message(
            f"{invoice.address}"
        )
        self.send_message(
            f"{invoice.amount}"
        )
        self.send_message(
            "Please push Paid when you done",
            reply_markup=self._build_markup()
        )

    def _deploy_invoice(self):
        i = self.invoice
        invoice = models.CryptoInvoice.objects.create(
            customer=i.customer,
            subscription=i.subscription,
            duration=i.duration,
            network=i.network,
            currency=i.currency,
            amount=i.amount,
        )
        return invoice

    def _build_markup(self):
        self.add_button(
            "Paid",
            reply_name="CryptoPayResultReply",
            args="PAID"            
        )
        self.add_button(
            "Cancel",
            reply_name="CryptoPayResultReply",
            args="CANCEL"
        )
        return self.markup


class CryptoInvoicePayingReplyBulder(CallbackInlineReplyBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.invoice = self.customer.crypto_invoices.filter(
            status__in=[
                "PAYING",
                "PAID",
            ],
        ).last()

        if self.invoice is None:
            self.out_of_route()

    def out_of_route(self):
        self.send_message(
            "You don't have current active invoice right now"
        )

        def build_replacement():
            # Bring curious customer back to right route
            self.router.redirect(
                app_name="main",
                reply_name="StartCommandReply",
                reply_type="COMMAND"
            )

        self.build = build_replacement


class CryptoPayResultReply(CryptoInvoicePayingReplyBulder):
    USING_ARGS = (
        "pay_status",
    )

    def build(self):
        pay_status = self._get_pay_status()
        if pay_status == "CANCEL":
            self.router.redirect(
                "CryptoPayCancelReply"
            )
        elif pay_status == "PAID":
            self.router.redirect(
                "CryptoPayDoneReply"
            )
        else:
            raise ValueError(
                f"Unsupported pay_status {pay_status}"        
            )
            
    def _get_pay_status(self):
        return self.callback.args[0]


class CryptoPayCancelReply(CryptoInvoicePayingReplyBulder):
    def build(self):
        self.customer.invoice.canceled()

        self.send_message(
            "Payment has been canceled"
        )

        return self.router.redirect(
            app_name="main",
            reply_name="StartCommandReply",
            reply_type="COMMAND"
        )


class CryptoPayDoneReply(CryptoInvoicePayingReplyBulder):
    def build(self):
        self._update_invoice()

        text = (
            "Thanks. We are checking your transaction now. "
        )

        self.send_message(
            text,
            reply_markup=self._build_markup()
        )

    def _update_invoice(self):
        self.invoice.status = "PAID"
        self.invoice.save()
    
    def _build_markup(self):
        self.add_button(
            "Check status now",
            reply_name="CryptoTranzCheckReply"
        )
        self.add_button(
            "Notify me when confirmed",
            reply_name="NotifyWhenTranzConfirmedReply"
        )
        return self.markup


class CryptoTranzCheckReply(CryptoInvoicePayingReplyBulder):
    def build(self):
        tranzes = self.invoice.transactions.all()
        if tranzes.count() == 0:
            return self.send_message(
                "Waiting for transaction. Still have not seen.",
                reply_markup=self._build_markup()
            )

        if tranzes.count() > 1:
            # TODO
            # Notify project admin/manager about this
            pass

        tranz = tranzes[0]
        if tranz.is_confirmed():
            self.invoice.confirmed()
            self.send_message(
                "Your transaction has been confirmed"
            )
            return self.router.redirect(
                app_name="accesser",
                reply_name="GiveInviteLinksReply",
                args=[
                    "c", # invoice code for crypto invoices
                    self.invoice.id,
                ]
            )
        else:
            self.send_message(
                (
                    f"We are hav been seen your transaction txid: {tranz.txid}\n\n"
                    "Confirmations\n"
                    f"Now: {tranz.current_confirmations} \n"  # Сейчас
                    f"Required: {tranz.required_confirmations}"  # Ожидается
                ),
                reply_markup=self._build_markup()
            )
            return

    def _build_markup(self):
        self.add_button(
            "Check confirmations now",
            reply_name="CryptoTranzCheckReply"
        )
        self.add_button(
            "Notify me when confirmed",
            reply_name="NotifyWhenTranzConfirmedReply"
        )
        return self.markup


class NotifyWhenTranzConfirmedReply(CryptoInvoicePayingReplyBulder):
    def build(self):
        self.send_message(
            "Sure! We will notify you when transaction be confirmed "
            "and will send you invite link"
        )
        # Notifications sends automatically by messenger worker
