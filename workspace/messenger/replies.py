import typing 
import hashlib
from django.conf import settings
from django.core.cache import cache
from django.template import Template, Context
from telebot import TeleBot
import telebot.types
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from .routers import Callback
from access_telebot.logger import get_logger

import main.models
from . import models


log = get_logger(__name__)
bot = TeleBot(settings.TELEBOT_KEY)



class Text:
    def __init__(
        self,
        text: str
    ):
        self.text = text

    def load(self):
        return self.text

    def context(self, **kwargs):
        template = Template(self.text)
        self.text = template.render(
            Context(kwargs)
        )
        return self
    
    # Text + Text concat ability
    def __add__(
        self, 
        other: typing.Union[
            'Text', str
        ]
    ) -> 'Text':
        if isinstance(other, Text):
            return Text(self.text + other.text)
        elif isinstance(other, str):
            return Text(self.text + other)
        return NotImplemented


class Translator:
    def __init__(self, translation_name: str):
        self.translation_name = translation_name

    def translate(
        self, 
        text: str, 
    ) -> Text:
        text = text.replace("\n", "\\n")
        translation = self._get_translation(text)\
            if settings.TRANSLATION is not None else text
        return Text(translation)
    
    def _get_translation(self, text: str) -> str:
        text = text.strip()
        translation = self._get_translation_from_cache(text)
        if translation is None:
            # Do not have translation in cache, check in DB
            translation = self._get_translation_from_db(text)
            if translation is None:
                # Do not have translation in DB 
                # So just set origin text without translation
                translation = text
        return translation
    
    def _get_translation_from_cache(self, text: str) -> typing.Optional[str]:
        cache_key = self._safe_cache_key(f'translation_{text}')
        translation = cache.get(cache_key)
        return translation
    
    def _save_translation_to_cache(self, text: str, translation: str):
        cache_key = self._safe_cache_key(f'translation_{text}')
        cache.set(cache_key, translation, timeout=3600)
    
    def _get_translation_from_db(self, text: str) -> typing.Optional[str]:
        try:
            translation_obj = models.Translation.objects.get(
                name=self.translation_name,
                from_text=text
            )
        except models.Translation.DoesNotExist:
            return None

        if translation_obj.to_text is None:
            return None
        
        translation = translation_obj.to_text
        self._save_translation_to_cache(text, translation)
        return translation
        
    @staticmethod
    def _safe_cache_key(key: str) -> str:
        # Использование MD5 для генерации уникального ключа
        # MD5 используется для простоты примера; SHA-256 предпочтительнее для реальных приложений
        return hashlib.md5(key.encode('utf-8')).hexdigest()


def translate(text: str) -> str:
    return Translator(
        settings.TRANSLATION
    ).translate(text)



class ReplyBuilder:
    markup: InlineKeyboardMarkup

    def add_button(
        self,
        caption: typing.Union[Text, str],
        app_name: typing.Optional[str] = None,
        reply_name: typing.Optional[str] = None,
        args: typing.Optional[
            typing.Union[list, str, int]
        ] = None
    ):
        if app_name is None:
            app_name = self.callback.app_name

        if reply_name is None:
            raise ValueError(
                "Arg reply_name is required"
            )

        if isinstance(caption, Text):
            caption_display = caption.load()
        elif isinstance(caption, str):
            caption_display = caption
        else:
            raise ValueError(
                f"Unsupported caption type: {type(caption)}"
            )

        callback = Callback.stringify(
            app_name, reply_name, args
        )
        self.markup.add(
            InlineKeyboardButton(
                caption_display, 
                callback_data=callback
            )
        ) 
        models.ShowedInlineButton.objects.update_or_create(
            callback_data=callback,
            defaults={
                "caption": caption_display, 
            }
        )

    def send_message(
        self, 
        message: typing.Union[Text, str], 
        *args, **kwargs
    ):
        if isinstance(message, Text):
            message_display = message.load()
        elif isinstance(message, str):
            message_display = message
        else:
            raise ValueError(
                f"Unsupported message type: {type(message)}"
            )
        message_display = message_display.replace("\\n", "\n")
        bot.send_message(
            self.customer.chat_id,
            text=message_display,
            parse_mode="HTML",
            *args, **kwargs
        )


class CallbackInlineReplyBuilder(ReplyBuilder):
    def __init__(
        self, 
        router: "CallbackInlineRouter"
        # customer: main.models.Customer, 
        # callback: telebot.types.CallbackQuery
    ):
        self.router = router
        self.customer = router.customer
        self.callback = router.callback
        self.markup = InlineKeyboardMarkup()


class CommandReplyBuilder(ReplyBuilder):
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: typing.Optional[
            telebot.types.Message
        ] = None,
    ):
        self.customer = customer
        self.message = message
        self.markup = InlineKeyboardMarkup()


class CustomReplyBuilder:

    def build_markup(
        self, 
        reply: models.CommandReply
    ) -> telebot.types.InlineKeyboardMarkup:
        buttons = reply.get_buttons()
        if not buttons.exists():
            log.info(f"Reply for <{reply}> has no buttons")
            return None

        # Создание инлайн-клавиатуры
        markup = InlineKeyboardMarkup()
        for button in buttons:
            # Добавление кнопки
            keyboard_button = InlineKeyboardButton(
                button.caption, 
                callback_data=button.reply.callback_data,
            )
            markup.add(keyboard_button)
            models.ShowedInlineButton.objects.update_or_create(
                callback_data=button.reply.callback_data,
                defaults={
                    "caption": button.caption, 
                }
            )
        return markup

        # callback = Callback.stringify(
        #     app_name, reply_name, args
        # )
        # self.markup.add(
        #     InlineKeyboardButton(
        #         caption_display, 
        #         callback_data=callback
        #     )
        # ) 
        # models.ShowedInlineButton.objects.update_or_create(
        #     callback_data=callback,
        #     defaults={
        #         "caption": caption_display, 
        #     }
        # )

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
            reply = models.CommandReply.objects.get(
                command=self._parse_command()
            )
        except models.CommandReply.DoesNotExist:
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
            reply = models.CallbackInlineReply.objects.get(
                callback_data=self.callback.stringify_self()
            )
        except models.CallbackInlineReply.DoesNotExist:  # Исправлена опечатка здесь
            bot.answer_callback_query(  # Используйте этот метод для отправки уведомления пользователю
                self.callback.id, 
                f"I don't know callback {self.callback.data}"
            )
            return

        # Используйте этот метод, чтобы сказать телеге, что сигнал от кнопки получен
        # bot.answer_callback_query(self.callback.id)
        
        # Используйте send_message для ответа в чат, а не reply_to
        bot.send_message(
            self.customer.chat_id,
            reply.text,
            reply_markup=self.build_markup(reply),
            parse_mode="HTML",
        )


