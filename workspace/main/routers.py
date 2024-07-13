from . import replies
from messenger.routers import (
    CommandRouterBase,
    CallbackInlineRouterBase,
)


class CommandRouter(CommandRouterBase):
    def route(self):
        _is = self.is_reply_name

        if _is("StartCommandReply"):
            return self.build_reply(replies.StartCommandReply)


class CallbackInlineRouter(CallbackInlineRouterBase):
    def route(self):
        _is = self.is_reply_name   

        if _is("StartReply"):
            return self.build_reply(replies.StartReply)

