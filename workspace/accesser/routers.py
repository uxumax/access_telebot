from . import replies
from messenger.routers import CallbackInlineRouterBase
from access_telebot.logger import get_logger


class CallbackInlineRouter(CallbackInlineRouterBase):
    replies = replies

