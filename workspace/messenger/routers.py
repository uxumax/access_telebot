from importlib import import_module
from access_telebot.logger import get_logger
import main.models
import telebot.types
import main.replies
import messenger.replies


class CallbackInlineRouterBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback


class CommandRouter:
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message,
        # command: str
    ):
        self.build_args = (customer, message)
        self.command = self._parse_command(message)

    def route(self):
        reply = self._get_reply()
        return reply(*self.build_args).build()
        
    def _parse_command(self, message: telebot.types.Message) -> str:
        command = message.text.split()[0][1:]  # Извлечение команды без '/'
        return command

    def _get_reply(self):
        def _is(command: str):
            return self.command == command        
        
        if _is("start"):
            return main.replies.CommandReplyStart        

        return messenger.replies.CustomCommandReply


class CallbackInlineRouter(CallbackInlineRouterBase):
    log = get_logger(__name__)

    def route(self):
        app_name = self._get_app_name()

        print("app_name", app_name)

        if app_name == "custom":
            return messenger.replies.CustomCallbackInlineReply(
                customer=self.customer,
                callback=self.callback                
            )

        router = self._get_app_router(app_name)

        print("router", router)

        if router is None:
            raise Exception(
                f"Cannot find app router by name: {app_name}"
            )
        return router(
            customer=self.customer,
            callback=self.callback
        ).route()

    def _get_app_name(self):
        app_name, _ = self.callback.data.split(":", 1)  # Разделяем callback.data на app_name и остальные данные
        return app_name

    def _get_app_router(self, app_name: str):
        try:
            app_module = import_module(f'{app_name}.routers')
        except (ImportError, AttributeError) as e:
            self.log.exception(
                f"Error loading module or class for app '{app_name}': {e}"
            )
            raise Exception(e)

        return getattr(app_module, 'CallbackInlineRouter')
