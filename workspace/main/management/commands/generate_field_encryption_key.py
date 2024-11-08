import os
import base64

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates a secure encryption key for FIELD_ENCRYPTION_KEY setting"

    def handle(self, *args, **kwargs):
        new_key = base64.urlsafe_b64encode(os.urandom(32))
        print(new_key.decode())
