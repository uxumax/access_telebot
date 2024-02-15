from importlib import import_module

import main.models
import telebot.types
import main.replies
import messenger.replies
from messenger.types import CallbackInlineRouterBase


class CommandRouter:
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message,
        command: str
    ):
        self.build_args = (customer, message)
        self.command = command

    def route(self):
        reply = self._get_reply()
        return reply(*self.build_args).build()
        
    def _get_reply(self):
        def _is(command: str):
            return self.command == command        
        
        if _is("start"):
            return main.replies.CommandReplyStart        

        return messenger.replies.CustomCommandReply


class CallbackInlineRouter(CallbackInlineRouterBase):
    def route(self):
        app_name = self._get_app_name()
        if app_name == "custom":
            return messenger.replies.CustomCallbackInlineReply(
                customer=self.customer,
                callback=self.callback                
            )

        router = self._get_app_router(app_name)
        return router(
            customer=self.customer,
            callback=self.callback
        ).route()

    def _get_app_name(self):
        app_name, _ = self.callback.data.split(":", 1)  # Разделяем callback.data на app_name и остальные данные
        return app_name

    def _get_app_router(self, app_name: str):
        try:
            # Пытаемся динамически загрузить модуль и получить доступ к классу CallbackInlineRouter
            app_module = import_module(f'{app_name}.routers')
            return getattr(app_module, 'CallbackInlineRouter')
        
        except (ImportError, AttributeError) as e:
            print(
                f"Error loading module or class for app '{app_name}': {e}"
            )
            return None  # Или другое действие по умолчанию

