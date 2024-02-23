from . import replies
from messenger.routers import CommandRouterBase


class CommandRouter(CommandRouterBase):
    def route(self):
        _is = self.is_reply_name

        if _is("StartCommandReply"):
            return self.build_reply(replies.StartCommandReply)
