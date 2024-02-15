import telebot
import typing

from messenger.replies import CommandReplyBuilderBase
from access_telebot.settings import TELEBOT_KEY


bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


CommandReply = typing.Union[
    'CommandReplyStart',
]


class CommandReplyStart(CommandReplyBuilderBase):
    def build(self):
        text = (
            "Hi. I am your accessbot"
        )

        bot.reply_to(
            self.message,
            text,
            reply_markup=self._build_markup()
        )        

    def _build_markup(self):
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton

        markup.add(
            button(
                "Plans", callback_data="cashier:all_subs"
            )
        )

        markup.add(
            button(
                "My plan", callback_data="cashier:my_subs"
            )
        )

        markup.add(
            button(
                "Contact", callback_data="raw_contact"
            )
        )

        return markup
