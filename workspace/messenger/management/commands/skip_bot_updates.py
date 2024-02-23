from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
import requests


class Command(BaseCommand):
    help = 'Clears all pending updates for the Telegram bot'

    def handle(self, *args, **kwargs):
        bot = telebot.TeleBot(settings.TELEBOT_KEY, parse_mode=None)

        bot.remove_webhook()
        
        url = f"https://api.telegram.org/bot{settings.TELEBOT_KEY}/getUpdates?offset=-1"
        requests.get(url)
        self.stdout.write(self.style.SUCCESS('Successfully cleared all bot updates.'))

