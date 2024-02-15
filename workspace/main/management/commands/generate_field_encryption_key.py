from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet


class Command(BaseCommand):
    help = "Generates a secure encryption key for FIELD_ENCRYPTION_KEY setting"

    def handle(self, *args, **kwargs):
        import os

        # Генерация ключа длиной 32 байта
        key = os.urandom(16)

        # Перевод ключа в шестнадцатеричную строку для удобства хранения
        key_hex = key.hex()

        print(key_hex)
        return
        key = Fernet.generate_key()
        safe_key = key.decode(
            "utf-8"
        )  # Конвертируем байты в строку для удобства копирования
        self.stdout.write(self.style.SUCCESS(f"Secure encryption key: {safe_key}"))
        self.stdout.write(
            self.style.SUCCESS(
                "Copy the above key into your settings.py as the value of FIELD_ENCRYPTION_KEY."
            )
        )
 
