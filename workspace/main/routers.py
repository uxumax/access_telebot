from . import replies
from messenger.routers import (
    CommandRouterBase,
    CallbackInlineRouterBase,
)


class CommandRouter(CommandRouterBase):
    replies = replies


class CallbackInlineRouter(CallbackInlineRouterBase):
    replies = replies

