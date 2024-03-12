import typing
# from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
# import json
import telebot
from . import models
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import messenger.replies
import messenger.routers
import messenger.models

from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger


log = get_logger(__name__)
bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


def _save_or_update_user(
    user: telebot.types.User,
    come_type: typing.Literal[
        "COMMAND",
        "CALLBACK",
    ],
) -> None:
    """
    Save or update the user information in the Customer model.
    """
    customer, _ = models.Customer.objects.get_or_create(chat_id=user.id)

    customer.username = user.username
    customer.is_bot = user.is_bot
    customer.first_name = user.first_name
    customer.last_name = user.last_name
    customer.language_code = getattr(user, "language_code", None)
    customer.is_premium = getattr(user, "is_premium", False)
    customer.added_to_attachment_menu = getattr(user, "added_to_attachment_menu", False)
    customer.can_join_groups = getattr(user, "can_join_groups", False)
    customer.can_read_all_group_messages = getattr(
        user, "can_read_all_group_messages", False
    )
    customer.supports_inline_queries = getattr(user, "supports_inline_queries", False)

    if come_type == "CALLBACK":
        customer.last_callback_inline_date = timezone.now()

    customer.save()

    return customer


def _is_message_command(message: telebot.types.Message) -> bool:
    return message.content_type == "text" and message.text.startswith("/")


class TooManyRequestsException(Exception):
    """Исключение, возникающее при слишком частых запросах пользователя."""

    pass


# class CallbackAntiFlooder:
#     def __init__(
#         self,
#         customer: telebot.types.User,
#     ):
#         self.customer = customer
#         self.log = get_logger(__name__)

#     def filter(self) -> None:
#         """Фильтр для проверки флуда."""
#         current_time = timezone.now()

#         last_callback_seconds = (
#             current_time - self.customer.last_callback_inline_date
#         ).total_seconds()

#         self.log.debug(
#             f"last_callback_seconds {last_callback_seconds} \n"
#             f"current_time {current_time} \n"
#             f"self.customer.last_callback_inline_date \
#                 {self.customer.last_callback_inline_date} \n"
#         )

#         # Проверяем, не слишком ли часто пользователь нажимает кнопку
#         if self.customer.last_callback_inline_date \
#                 and last_callback_seconds < 1:
#             raise TooManyRequestsException(
#                 "Too many requests in a short period of time"
#             )


class InlineCallbackFirstHandler:
    def __init__(self, callback: telebot.types.CallbackQuery):
        self.callback = callback
        self._answer_to_callback()
        self._set_selected_button()

    def _answer_to_callback(self):
        try:
            bot.answer_callback_query(self.callback.id)
        except telebot.apihelper.ApiTelegramException:
            log.warning(
                f"Answer to callback:{self.callback.data} has got timeout error"
            )

    def _set_selected_button(self):
        try:
            bot.edit_message_text(
                chat_id=self.callback.message.chat.id,
                message_id=self.callback.message.message_id,
                text=self._get_edited_text(),
                reply_markup=None,
            )
        except Exception as e:
            msg = self.callback.message
            log.exception(f"Cannot set selected button to message {msg}: {e}")

    def _get_edited_text(self):
        current_text = self.callback.message.text
        button_caption = self._get_button_caption()
        new_text = f"{current_text}\n_________\n{button_caption}"
        return new_text

    def _get_button_caption(self):
        ShowedInlineButton = messenger.models.ShowedInlineButton
        try:
            showed_button = ShowedInlineButton.objects.get(
                callback_data=self.callback.data
            )
        except ShowedInlineButton.DoesNotExist:
            self.warning(
                "Cannot set selected button coz callback_data "
                "not exists in messenger.ShowedInlineButton model records"
            )
            raise ShowedInlineButton.DoesNotExist()
        return showed_button.caption


@bot.callback_query_handler(func=lambda callback: True)
def callback_inline_handler(callback: telebot.types.CallbackQuery) -> None:
    InlineCallbackFirstHandler(callback)
    customer = _save_or_update_user(callback.from_user, "CALLBACK")
    messenger.routers.route_callback_inline(customer, callback)


@bot.message_handler(func=lambda message: _is_message_command(message))
def command_handler(message: telebot.types.Message):
    customer = _save_or_update_user(message.from_user, "COMMAND")
    # messenger.routers.CommandRouter(customer, message).route()
    messenger.routers.route_command(customer, message)


# General handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: telebot.types.Message) -> None:
    _save_or_update_user(message.from_user)
    bot.reply_to(
        message, f"Your message is {message.text} but I don't know what to do with this"
    )


class TelegramWebhookShield:
    def __init__(self, update):
        self.update = update

    def is_message_from_another_bot(self):
        try:
            return self.update.message.from_user.is_bot
        except AttributeError:
            return False


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):
    def get(self, request):
        return HttpResponse("Webhook url test")

    def post(self, request):
        update = self._decode_update(request)
        log.info(f"UPDATE:\n{update}")

        if self._is_skip_update(update):
            return JsonResponse({"status": 200})

        shield = TelegramWebhookShield(update)
        if shield.is_message_from_another_bot():
            bot.send_message(
                update.message.chat.id, 
                "Sorry, I cannot speak with other bots"
            )
            return JsonResponse({"status": 200})

        # Обработка обновлений о статусе члена чата
        self._process_chat_member_update(update)

        bot.process_new_updates([update])

        return JsonResponse({"status": 200})

    @staticmethod
    def _decode_update(request):
        json_str = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_str)
        return update

    def _is_skip_update(self, update):
        # Обновление не пропускается, если это приватное сообщение
        private_message = self._is_private_message(update)
        # Обновление не пропускается, если это запрос обратного вызова
        callback_query = self._is_callback_query(update)
        # Обновление не пропускается, если это изменение статуса члена чата
        chat_member_update = hasattr(update, "my_chat_member")
        
        # Если обновление не относится ни к одному из вышеуказанных типов, оно пропускается
        return not (private_message or callback_query or chat_member_update)

    def _process_chat_member_update(self, update):
        # Проверяем, есть ли обновление статуса члена чата
        if not hasattr(update, "my_chat_member"):
            return
        # Получаем данные обновления
        new_status = update.my_chat_member.new_chat_member.status
        if new_status in ["administrator", "creator"]:
            # Сохраняем или обновляем информацию о чате
            chat_info = update.my_chat_member.chat
            chat_type = models.ChatTypeChoices.SUPERGROUP \
                if chat_info.type == "supergroup" else models.ChatTypeChoices.GROUP
            models.Chat.objects.update_or_create(
                chat_id=chat_info.id,
                defaults={
                    "title": chat_info.title or "",
                    "chat_type": chat_type,
                    "invite_link": ""
                }
            )

    @staticmethod
    def _is_private_message(update) -> bool:
        is_message = hasattr(update, "message") and update.message
        if is_message:
            if update.message.chat.type == "private":
                return True
        return False

    @staticmethod
    def _is_callback_query(update) -> bool:
        return hasattr(update, "callback_query") and update.callback_query
