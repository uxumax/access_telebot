import main.models
import telebot.types

from . import replier_main
from . import replier_custom

MAIN_COMMANDS = [
    "start",
]

MAIN_CALLBACK_INLINES = [
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
        if self.command in MAIN_COMMANDS:
            return self._route_to_main_replier()
        else:
            return self._route_to_custom_replier()

    def _parse_command(self) -> str:
        command = self.message.text.split()[0][1:]  # Извлечение команды без '/'
        return command

    def _route_to_main_replier(self):
        return replier_main.CommandRouter(
            self.customer, self.message, self.command
        ).route()

    def _route_to_custom_replier(self):
        return replier_custom.CommandReply(
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
        if self.callback.data in MAIN_CALLBACK_INLINES:
            return self._route_to_main_replier()
        else:
            return self._route_to_custom_replier()

    def _route_to_main_replier(self):
        return replier_main.CallbackInlineRouter(
            self.customer, self.callback
        ).route()

    def _route_to_custom_replier(self):
        return replier_custom.CallbackInlineReply(
            self.customer, self.callback
        ).build()
