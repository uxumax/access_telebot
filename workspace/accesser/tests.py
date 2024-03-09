from django.test import TestCase
from decimal import Decimal
from datetime import timedelta
from . import models 


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

