from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

import typing

from messenger.replies import CommandReplyBuilder
from messenger.routers import Callback

from access_telebot.settings import TELEBOT_KEY


bot = TeleBot(TELEBOT_KEY)


CommandReply = typing.Union[
    'StartCommandReply',
]


class StartCommandReply(CommandReplyBuilder):
    def build(self):
        text = (
            "Hi. I am your accessbot"
        )
       
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )

    def _build_markup(self):
        self.add_button(
            "Plans",
            app_name="accesser",
            reply_name="AllSubsReply"
        )

        return self.markup

        # markup.add(
        #     InlineKeyboardButton(
        #         "Plans", callback_data="accesser:AllSubsReply"
        #     )
        # )
        
        # markup.add(
        #     InlineKeyboardButton(
        #         "My plan", callback_data="accesser:MySubsReply"
        #         )
        #     )
        
        # markup.add(
        #     InlineKeyboardButton(
        #         "Contact", callback_data="raw_contact"
        #     )
        # )

        return markup
