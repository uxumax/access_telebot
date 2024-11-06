from . import replies
from messenger.routers import CallbackInlineRouterBase


class CallbackInlineRouter(CallbackInlineRouterBase):
    replies = replies
