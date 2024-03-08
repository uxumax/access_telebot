from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.conf import settings

from . import models
import main.models
import accesser.models
import accesser.tests
from cashier import replies 
from messenger.replies import Callback
from messenger.routers import CallbackInlineRouter
from messenger.routers import build_callback_inline_reply 


if settings.TESTER_CHAT_ID is None:
    raise ValueError(
        "Please set TESTER_CHAT_ID in access_telebot/settings_local.py. "
        "Do not forget add bot to this tester contact list"
    )


class MockModelCreator:
    @classmethod
    def BuildingInvoice(cls, **kwargs):
        subscription = accesser.tests.MockModelCreator\
            .Subscription()
        subscription.save()
        return models.BuildingInvoice(
            customer=kwargs["customer"],
            subscription=subscription,
            duration=subscription.durations.first()
            # **kwargs
        )

    @classmethod
    def CryptoTransaction(cls, **kwargs):
        return models.CryptoTransaction(
            invoice=kwargs["invoice"],
            txid=kwargs.get("txid", "txid_test_123"),
            current_confirmations=kwargs.get(
                "current_confirmations", 0
            ),
            required_confirmations=kwargs.get(
                "required_confirmations", 19
            )
        )

    @classmethod
    def CryptoInvoice(cls, **kwargs):
        building_invoice = cls.BuildingInvoice(
            customer=kwargs["customer"]
        )
        building_invoice.save()
        subscription = building_invoice.subscription
        duration = subscription.durations.first()

        return models.CryptoInvoice( 
            customer=kwargs["customer"],
            subscription=subscription,
            duration=duration,
            amount=Decimal("20"),
            network="TRON",
            address="TRonAdDreSs...",
            currency="USDT",
            expire_date=timezone.now() + duration.duration
        )  


class CashierReplyTestCase(TestCase):
    fixtures = ['messenger/fixtures/translations.json']

    def setUp(self):
        self.customer = main.models.Customer(
            chat_id=settings.TESTER_CHAT_ID
        )
        self.customer.save()

    def prepare_reply(
        self,
        reply_name: str, 
        args: list = None
    ):
        router = CallbackInlineRouter(
            customer=self.customer,
            callback=Callback(
                id=1,
                app_name="cashier",
                reply_name=reply_name,
                args=args
            )
        )
        return eval(f"replies.{reply_name}(router)")
        # return CryptoPayingReply(router)


class TestChooseAccessDurationReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        invoice = MockModelCreator.BuildingInvoice(
            customer=self.customer
        )
        self.reply = self.prepare_reply(
            "ChooseAccessDurationReply",
            args=[
                invoice.subscription.id
            ]
        )

    def test(self):
        self.reply.build()
        

class TestChoosePayMethodReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        invoice = MockModelCreator.BuildingInvoice(
            customer=self.customer
        )
        self.reply = self.prepare_reply(
            "ChoosePayMethodReply", 
            args=[
                invoice.duration.id
            ]
        )

    def test(self):
        self.reply.build()

class TestCheckoutReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        MockModelCreator.BuildingInvoice(
            customer=self.customer
        )
        self.reply = self.prepare_reply(
            "CheckoutReply", [
                "usdt_trc20",
            ]
        )

    def test(self):
        self.reply.build()


class TestCryptoPayingReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        self.invoice = MockModelCreator.CryptoInvoice(
            customer=self.customer
        )
        self.reply = self.prepare_reply("CryptoPayingReply")

    @patch('cashier.replies.CryptoPayingReply._deploy_invoice')  # Adjust the path to match where _deploy_invoice is
    def test(self, mock_deploy_invoice):
        mock_deploy_invoice.return_value = self.invoice  
        self.reply.build()


class TestCryptoPayCancelReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        MockModelCreator.CryptoInvoice(
            customer=self.customer,
            status="PAYING"
        ).save()
        self.reply = self.prepare_reply("CryptoPayCancelReply")
        
    def test(self):
        self.reply.build()


class TestCryptoPayDoneReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        MockModelCreator.CryptoInvoice(
            customer=self.customer,
            status="PAYING"
        ).save()
        self.reply = self.prepare_reply("CryptoPayDoneReply")
        
    def test(self):
        self.reply.build()


class TestCryptoTranzWaitReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp(), 
        invoice = MockModelCreator.CryptoInvoice(
            customer=self.customer,
            status="PAID"
        ).save()
        self.transaction = MockModelCreator.CryptoTransaction(
            invoice=invoice
        )
        # Do not save transaction now coz for check Reply with exiting tranz or not
        self.reply = self.prepare_reply("CryptoTranzWaitReply")
        
    def test(self):
        self.reply.build()


class TestCryptoConfirmWaitReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        invoice = MockModelCreator.CryptoInvoice(
            customer=self.customer,
            status="PAID"
        )
        invoice.save()
        self.transaction = MockModelCreator.CryptoTransaction(
            invoice=invoice,
            current_confirmations=18,
            required_confirmations=19
        )
        self.transaction.save()
        self.reply = self.prepare_reply(
            "CryptoConfirmWaitReply",
            args=[
                self.transaction.id,
            ]
        )
        
    def test(self):
        self.reply.build()


class TestNotifyWhenTranzConfirmedReply(CashierReplyTestCase):
    def setUp(self):
        super().setUp()
        MockModelCreator.CryptoInvoice(
            customer=self.customer,
            status="PAID"
        ).save()
        self.reply = self.prepare_reply("NotifyWhenTranzConfirmedReply")
        
    def test(self):
        self.reply.build()

