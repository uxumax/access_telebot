from django.core.management.base import BaseCommand
from access_telebot.settings import TELEBOT_KEY
import telebot

bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


def get_channel_name(chat_id: int | str) -> str:
    chat: telebot.types.Chat = bot.get_chat(chat_id)
    return chat.title  # This is the title of the channel


class Command(BaseCommand):
    help = "Some fast temp cmd"

    def handle(self, *args, **options):
        name = get_channel_name(-1002040160842)
        print(name)