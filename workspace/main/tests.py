from django.test import TestCase
import random

from . import models 


class TestUtils:
    def generate_random_int_id() -> int:
        return random.randint(int(1e9), int(1e10) - 1)


class MockModelCreator:
    @staticmethod
    def Customer(**kwargs):
        customer = models.Customer(
            chat_id=kwargs.get("chat_id", TestUtils.generate_random_int_id())
        )
        customer.save()
        return customer


