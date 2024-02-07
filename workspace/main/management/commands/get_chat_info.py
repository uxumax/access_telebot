from django.core.management.base import BaseCommand, CommandError
from telebot import TeleBot
from telebot.types import Chat
from django.conf import settings


class Command(BaseCommand):
    help = 'Retrieves all available information about a specified chat'
    
    def add_arguments(self, parser):
        parser.add_argument('chat_id', type=str, help='The chat ID to retrieve information for')

    def handle(self, *args, **options):
        chat_id = options['chat_id']
        bot = self.initialize_bot()
        chat_info = self.get_all_chat_info(bot, chat_id)
        self.print_chat_info(chat_info)

    def initialize_bot(self) -> TeleBot:
        """Initialize the Telegram bot."""
        return TeleBot(settings.TELEBOT_KEY)

    def get_all_chat_info(self, bot: TeleBot, chat_id: str) -> dict:
        """Retrieve all available information about the chat."""
        chat: Chat = bot.get_chat(chat_id)
        chat_info = {
            attr: getattr(chat, attr, None) 
            for attr in dir(chat) 
            if not attr.startswith('__') and not callable(getattr(chat, attr))
        }
        return chat_info

    def print_chat_info(self, chat_info: dict):
        """Print out all the information about the chat."""
        for key, value in chat_info.items():
            self.stdout.write(self.style.SUCCESS(f"{key}: {value}"))
