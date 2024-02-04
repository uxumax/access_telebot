from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import json
import telebot
import main.models
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import messenger.replier

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

    return customer


def _is_message_command(message: telebot.types.Message) -> bool:
    return message.content_type == 'text' and message.text.startswith('/')


class TooManyRequestsException(Exception):
    """Исключение, возникающее при слишком частых запросах пользователя."""
    pass


class CallbackAntiFlooder:
    def __init__(
        self, 
        customer: telebot.types.User,
    ):
        self.customer = customer
        self.log = get_logger(__name__)

    def filter(self) -> None:
        """Фильтр для проверки флуда."""
        current_time = timezone.now()

        last_callback_seconds = (
            current_time - self.customer.last_callback_inline_date
        ).total_seconds()

        self.log.debug(
            f"last_callback_seconds {last_callback_seconds} \n"
            f"current_time {current_time} \n"
            f"self.customer.last_callback_inline_date \
                {self.customer.last_callback_inline_date} \n"
        )

        # Проверяем, не слишком ли часто пользователь нажимает кнопку
        if self.customer.last_callback_inline_date \
                and last_callback_seconds < 2: 
            raise TooManyRequestsException(
                "Too many requests in a short period of time"
            )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_handler(call: telebot.types.CallbackQuery) -> None:
    customer = _save_or_update_user(call.from_user)

    try:
        anti_flooder = CallbackAntiFlooder(customer)
        anti_flooder.filter()
    except TooManyRequestsException:
        # Ответ на callback query с уведомлением о слишком частых запросах
        bot.answer_callback_query(call.id, text="Не нажимайте так часто!")
        return

    customer.update_last_callback_inline_date()
    messenger.replier.handle_callback_inline(customer, call)
    

@bot.message_handler(func=lambda message: _is_message_command(message))
def command_handler(message: telebot.types.Message):
    customer = _save_or_update_user(message.from_user)
    messenger.replier.handle_command(customer, message)


# General handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: telebot.types.Message) -> None:
    customer = _save_or_update_user(message.from_user)
    bot.reply_to(
        message, 
        f"Your message is {message.text} but I don't know what to do with this"
    )


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
