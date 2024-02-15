from importlib import import_module

import main.models
import telebot.types
import main.replies
import messenger.replies


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


class CallbackInlineRouter:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery,
    ):
        self.customer = customer
        self.callback = callback

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


# class CommandRouter:
#     def __init__(
#         self,
#         customer: main.models.Customer, 
#         message: telebot.types.Message
#     ):
#         self.customer = customer
#         self.message = message
#         self.command = self._parse_command()

#     def route(self):
#         if self.command in MAIN_COMMANDS:
#             return self._route_to_main_replier()
#         else:
#             return self._route_to_custom_replier()

#     def _parse_command(self) -> str:
#         command = self.message.text.split()[0][1:]  # Извлечение команды без '/'
#         return command

#     def _route_to_main_replier(self):
#         return replier_main.CommandRouter(
#             self.customer, self.message, self.command
#         ).route()

#     def _route_to_custom_replier(self):
#         return replier_custom.CommandReply(
#             self.customer, self.message, self.command
#         ).build()


# class CallbackInlineRouter:
#     def __init__(
#         self,
#         customer: main.models.Customer, 
#         callback: telebot.types.CallbackQuery
#     ):
#         self.customer = customer
#         self.callback = callback

#     def route(self):
#         if self.callback.data in MAIN_CALLBACK_INLINES:
#             return self._route_to_main_replier()
#         else:
#             return self._route_to_custom_replier()

#     def _route_to_main_replier(self):
#         return replier_main.CallbackInlineRouter(
#             self.customer, self.callback
#         ).route()

#     def _route_to_custom_replier(self):
#         return replier_custom.CallbackInlineReply(
#             self.customer, self.callback
#         ).build()
