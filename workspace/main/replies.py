import typing
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from messenger.replies import (
    CommandReplyBuilder,
    translate as _,
)
from messenger.routers import Callback
from access_telebot.settings import TELEBOT_KEY


bot = TeleBot(TELEBOT_KEY)
CommandReply = typing.Union[
    'StartCommandReply',
]


class StartCommandReply(CommandReplyBuilder):
    def build(self):
        text = _(
            "Hi. I am accessbot. "
            "I can provide access to some private telegram channels. "
            "Check Plans below for more info. "
        )       
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )

    def _build_markup(self):
        self.add_button(
            _("Plans"),
            app_name="accesser",
            reply_name="AllSubsReply"
        )
        self.add_button(
            _("My plan"),
            app_name="accesser",
            reply_name="MySubsReply"
        )
        return self.markup

