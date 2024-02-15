from . import replies
import telebot
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
from messenger.types import CallbackInlineRouterBase


bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


class CallbackInlineRouter(CallbackInlineRouterBase):

    def route(self):
        def _is(data: str):
            return self.callback.data == data        
        
        if _is("accesser:my_subs"):
            return self._build_reply(replies.InlineReplyMySubs)

        if _is("accesser:all_subs"):
            return self._build_reply(replies.InlineReplyAllSubs)

        bot.answer_callback_query(
            self.callback.id, 
            f"I don't know callback {self.callback.data}"
        )

    def _build_reply(
        self, 
        InlineReply: replies.CallbackInlineReply
    ):
        bot.answer_callback_query(self.callback.id)
        return InlineReply(
            self.customer, self.callback
        ).build()