from . import replies
from telebot import TeleBot
from django.conf import settings
from access_telebot.logger import get_logger
from messenger.routers import CallbackInlineRouterBase

bot = TeleBot(settings.TELEBOT_KEY)
log = get_logger(__name__)


class CallbackInlineRouter(CallbackInlineRouterBase):

    def route(self):
        _is = self.is_reply_name

        if _is("ChooseSubscriptionReply"):
            return self.build_reply(replies.ChooseSubscriptionReply)

        if _is("MySubscriptionsReply"):
            return self.build_reply(replies.MySubscriptionsReply)

        if _is("GiveInviteLinksReply"):
            return self.build_reply(replies.GiveInviteLinksReply)

        if _is("RevokeAccessNotificationReply"):
            return self.build_reply(replies.RevokeAccessNotificationReply)

        return self.reply_not_found()

