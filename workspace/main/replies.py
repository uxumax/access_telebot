import typing
from telebot import TeleBot
from messenger.replies import (
    CommandReplyBuilder,
    CallbackInlineReplyBuilder,
    translate as _,
)
from access_telebot.settings import TELEBOT_KEY


bot = TeleBot(TELEBOT_KEY)
CommandReply = typing.Union[
    'StartCommandReply',
]


class StartCommandReply(CommandReplyBuilder):
    def build(self):
        text = _(
            "Hi. I am AccessBot. "
            "I can provide access to some private Telegram channels. "
            "Check the 'Plans' below for more info."
        )       
        self.send_message(
            text,
            reply_markup=self._build_markup()
        )

    def _build_markup(self):
        self.add_button(
            _("Plans"),
            app_name="accesser",
            reply_name="ChatGroupsReply"
        )
        self.add_button(
            _("My plan"),
            app_name="accesser",
            reply_name="MySubsReply"
        )
        return self.markup


class StartReply(CallbackInlineReplyBuilder):
    def build(self):
        return self.router.redirect(
            app_name="main",
            reply_name="StartCommandReply",
            reply_type="COMMAND"
        )
