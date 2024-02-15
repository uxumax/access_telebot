from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Generates a secure encryption key for FIELD_ENCRYPTION_KEY setting'

    def handle(self, *args, **kwargs):
        key = Fernet.generate_key()
        safe_key = key.decode('utf-8')  # Конвертируем байты в строку для удобства копирования
        self.stdout.write(self.style.SUCCESS(f'Secure encryption key: {safe_key}'))
        self.stdout.write(self.style.SUCCESS('Copy the above key into your settings.py as the value of FIELD_ENCRYPTION_KEY.'))
