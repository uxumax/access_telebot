from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
import telebot
import main.models

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger


log = get_logger(__name__)
bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


def _save_or_update_user(user: telebot.types.User) -> None:
    """
    Save or update the user information in the Customer model.
    """
    customer, _ = main.models.Customer.objects.get_or_create(
        chat_id=user.id
    )
    customer.username = user.username
    customer.is_bot = user.is_bot
    customer.first_name = user.first_name
    customer.last_name = user.last_name
    customer.language_code = getattr(user, 'language_code', None)
    customer.is_premium = getattr(user, 'is_premium', False)
    customer.added_to_attachment_menu = getattr(user, 'added_to_attachment_menu', False)
    customer.can_join_groups = getattr(user, 'can_join_groups', False)
    customer.can_read_all_group_messages = getattr(user, 'can_read_all_group_messages', False)
    customer.supports_inline_queries = getattr(user, 'supports_inline_queries', False)
    customer.save()


@bot.message_handler(commands=['start'])
def handle_start(message: telebot.types.Message) -> None:
    bot.reply_to(message, "Hi. You have been pushed Start now")


# General handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: telebot.types.Message) -> None:
    _save_or_update_user(message.from_user)
    bot.reply_to(message, "Your message: " + message.text)


class TelegramWebhookShield:
    def __init__(self, update):
        self.update = update

    def is_message_from_another_bot(self):
        try:
            return self.update.message.from_user.is_bot
        except AttributeError:
            return False


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    @staticmethod
    def _decode_update(request):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        return update

    def get(self, request):
        return HttpResponse("Webhook url test")

    def post(self, request):
        update = self._decode_update(request)

        shield = TelegramWebhookShield(update)
        if shield.is_message_from_another_bot():
            bot.send_message(
                update.message.chat.id,
                "Sorry, I cannot speak with other bots"
            )
            return

        # bot.send_message(
        #     update.message.chat.id,
        #     "Test"
        # )

        bot.process_new_updates([update])

        return JsonResponse({'status': 200})