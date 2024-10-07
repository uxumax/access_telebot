from django.core.management.base import BaseCommand, CommandError
from telebot import TeleBot
from telebot.types import Chat
from django.conf import settings


bot = TeleBot(settings.TELEBOT_KEY)


class Command(BaseCommand):
    help = 'Unban chat member (and his invite links?)'
    
    def add_arguments(self, parser):
        parser.add_argument('chat_id', type=str)
        parser.add_argument('user_id', type=str)

    def handle(self, *args, **options):
        chat_id = options['chat_id']
        user_id = options['user_id']
        bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
        self.stdout.write(self.style.SUCCESS(
            f"User {user_id} has been unbanned in chat {chat_id}")
        )
