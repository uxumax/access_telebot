import main.models
import telebot.types

from . import replier_dynamic
from . import replier_static


STATIC_COMMANDS = [
    "start",
]

STATIC_CALLBACK_INLINES = [
    "my_subs",
    "all_subs",
]


class CommandRouter:
    def __init__(
        self,
        customer: main.models.Customer, 
        message: telebot.types.Message
    ):
        self.customer = customer
        self.message = message
        self.command = self._parse_command()

    def route(self):
        if self.command in STATIC_COMMANDS:
            return self._route_to_static_reply()
        else:
            return self._route_to_dyncamic_reply()

    def _parse_command(self) -> str:
        command = self.message.text.split()[0][1:]  # Извлечение команды без '/'
        return command

    def _route_to_static_reply(self):
        return replier_static.StaticCommandRouter(
            self.customer, self.message, self.command
        ).route()

    def _route_to_dyncamic_reply(self):
        return replier_dynamic.CommandReply(
            self.customer, self.message, self.command
        ).build()


class CallbackInlineRouter:
    def __init__(
        self,
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback

    def route(self):
        if self.callback.data in STATIC_CALLBACK_INLINES:
            return self._route_to_static_reply()
        else:
            return self._route_to_dyncamic_reply()

    def _route_to_static_reply(self):
        return replier_static.StaticCallbackInlineRouter(
            self.customer, self.callback
        ).route()

    def _route_to_dyncamic_reply(self):
        return replier_dynamic.CallbackInlineReply(
            self.customer, self.callback
        ).build()
