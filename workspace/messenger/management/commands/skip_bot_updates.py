from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
import requests

from main.workers import webhook_tunneler
import main.models


class Command(BaseCommand):
    help = 'Clears all pending updates for the Telegram bot'

    def handle(self, *args, **kwargs):
        bot = telebot.TeleBot(settings.TELEBOT_KEY, parse_mode=None)
        # bot.remove_webhook(drop_pending_updates=True)
        bot.delete_webhook(drop_pending_updates=True)

        # Set webhook back
        webhook_url = self._get_webhook_url()
        bot.set_webhook(url=webhook_url) 

        self.stdout.write(self.style.SUCCESS('Successfully cleared all bot updates.'))

    def _get_webhook_url(self) -> str:
        webhook = main.models.TelegramWebhook.load()
        return webhook.url

