import telebot
import typing 
from importlib import import_module

from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger

import main.models
import accesser.models
import messenger.models


log = get_logger(__name__)
bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


class CallbackInlineReplyBuilderBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback


class CommandReplyBuilderBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message,
    ):
        self.customer = customer
        self.message = message


class CustomReplyBuilder:
    log = get_logger(__name__)

    def build_markup(
        self, 
        reply: messenger.models.CommandReply
    ) -> telebot.types.InlineKeyboardMarkup:
        buttons = reply.get_buttons()
        if not buttons.exists():
            self.log.info(f"Reply for <{reply}> has no buttons")
            return None

        # Создание инлайн-клавиатуры
        markup = telebot.types.InlineKeyboardMarkup()
        for button in buttons:
            # Добавление кнопки
            button = telebot.types.InlineKeyboardButton(
                button.caption, callback_data=button.reply.callback_data,
            )
            markup.add(button)
        return markup


class CustomCommandReply(CustomReplyBuilder):
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message
    ):
        self.customer = customer
        self.message = message

    def build(self):
        try:
            reply = messenger.models.CommandReply.objects.get(
                command=self._parse_command()
            )
        except messenger.models.CommandReply.DoesNotExists:
            bot.reply_to(
                self.message, 
                f"I don't know command {self.message.text}"
            )
            return

        bot.reply_to(
            self.message,
            reply.text,
            reply_markup=self.build_markup(reply)
        )

    def _parse_command(self) -> str:
        command = self.message.text.split()[0][1:]  # Извлечение команды без '/'
        return command


class CustomCallbackInlineReply(CustomReplyBuilder):
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback

    def build(self):
        try:
            reply = messenger.models.CallbackInlineReply.objects.get(
                callback_data=self.callback.data
            )
        except messenger.models.CallbackInlineReply.DoesNotExist:  # Исправлена опечатка здесь
            bot.answer_callback_query(  # Используйте этот метод для отправки уведомления пользователю
                self.callback.id, 
                f"I don't know callback {self.callback.data}"
            )
            return

        # Используйте этот метод, чтобы сказать телеге, что сигнал от кнопки получен
        bot.answer_callback_query(self.callback.id)
        
        # Используйте send_message для ответа в чат, а не reply_to
        bot.send_message(
            self.callback.message.chat.id,  # Получаем ID чата из callback.message
            reply.text,
            reply_markup=self.build_markup(reply)
        )

