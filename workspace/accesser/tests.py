from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from types import SimpleNamespace
import main.tests

from access_telebot.settings import (
    NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE,
    WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS,
)
from . import models 

from accesser.workers import (
    customer_access_revoker,
)


class MockModelCreator: 
    @classmethod
    def Subscription(cls, **kwargs):
        subscription = models.Subscription(
            name="Test Plan"
        )
        subscription.save()
        duration = cls.SubscriptionDurationPrice(
            subscription=subscription,
            price=Decimal("20"),
        )
        duration.save()
        return subscription
        
    @staticmethod
    def SubscriptionDurationPrice(**kwargs):
        return models.SubscriptionDurationPrice(
            subscription=kwargs["subscription"],
            price=kwargs.get("price", Decimal("20")),
            duration=kwargs.get("duration", timedelta(days=30))
        )

    @staticmethod
    def CustomerChatAccess(**kwargs):
        access = models.CustomerChatAccess(
            customer=main.tests.MockModelCreator.Customer(),
            start_date=kwargs.get(
                "start_date", timezone.now() - timedelta(days=3)
            ),
            end_date=kwargs.get(
                "end_date", timezone.now() + timedelta(days=4)
            ),
            subscription=kwargs.get(
                "subscription", MockModelCreator.Subscription()
            )
        )
        access.save()
        return access


class CustomerAccessRevokerWorkerTest(TestCase):

    @staticmethod
    def _make_access(end_date):
        return MockModelCreator.CustomerChatAccess(
            end_date=end_date
        )

    def setUp(self):
        # self.start_expiring_date = (
        #     expire_date - NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE
        # )
        # self.revoke_date = (
        #     expire_date + WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS
        # )

        now = timezone.now()
        self.accesses = SimpleNamespace(
            before_expiring=self._make_access(
                now + timedelta(days=3),
            ),
            expiring=self._make_access( 
                # If NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE==2 days
                # Better set 47 hours
                now + timedelta(hours=47),
            ),
            expired=self._make_access(
                now - timedelta(minutes=1)
            ),
            revoking=self._make_access(
                # now - timedelta(days=6)
                now - WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS
            )
        )

        # Set worker
        self.worker = customer_access_revoker.Worker()
        self.worker._refresh_expiring_range()
            
    def test_get_expiring_accesses(self):
        expiring_accesses = self.worker._get_expiring_accesses()
        # print(expiring_accesses)
        self.assertNotIn(self.accesses.before_expiring, expiring_accesses)
        self.assertIn(self.accesses.expiring, expiring_accesses)
        self.assertIn(self.accesses.expired, expiring_accesses)
        self.assertNotIn(self.accesses.revoking, expiring_accesses)

    def test_get_accesses_for_revoke(self):
        revoking_accesses = self.worker._get_accesses_for_revoke()
        # print(revoking_accesses)
        self.assertNotIn(self.accesses.before_expiring, revoking_accesses)
        self.assertNotIn(self.accesses.expiring, revoking_accesses)
        self.assertNotIn(self.accesses.expired, revoking_accesses)
        self.assertIn(self.accesses.revoking, revoking_accesses)

        

