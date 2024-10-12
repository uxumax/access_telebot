import typing
import messenger.types
from types import SimpleNamespace
from importlib import import_module
from telebot import TeleBot
from django.conf import settings
from django.db import transaction
from access_telebot.logger import get_logger
import main.models
import telebot.types


bot = TeleBot(settings.TELEBOT_KEY)
log = get_logger(__name__)


class ReplyTypeConverter:
    COMMAND = "1"
    CALLBACK = "2"

    @classmethod
    def decode(cls, code: str) -> messenger.types.ReplyType:
        if code == "1":
            return "COMMAND"
        elif code == "2":
            return "CALLBACK"
        else:
            raise ValueError(f"Unsupported reply_code {code}")

    @classmethod
    def encode(cls, reply_type: messenger.types.ReplyType) -> int:
        if reply_type == "COMMAND":
            return cls.COMMAND
        elif reply_type == "CALLBACK":
            return cls.CALLBACK
        else:
            raise ValueError(
                f"Unsupported reply_type {reply_type}"
            )


class Callback:
    def __init__(
        self,
        id: int,
        app_name: str,
        reply_name: str,
        args: typing.Union[
            list, int, str
        ] = None,
        reply_type: messenger.types.ReplyType = "CALLBACK",
    ):
        self.id = id
        self.app_name = app_name
        self.reply_type = reply_type
        self.reply_name = reply_name
        self.args = args

    def stringify_self(self):
        if self.reply_type == "CALLBACK":
            reply_code = 2
        elif self.reply_type == "COMMAND":
            reply_code = 1
        else:
            raise ValueError(
                "Unsupported Callback reply_type"
            )
        return (
            f"{self.app_name}&{reply_code}&{self.reply_name}"
        ) # TODO add arguments stringify

    @classmethod
    def stringify(
        cls,
        app_name: str,
        reply_name: str,
        args: typing.Union[
            list, str, int,
        ] = None,
        reply_type: messenger.types.ReplyType = "CALLBACK",
    ):

        reply_code = ReplyTypeConverter.encode(reply_type)
        line = f"{app_name}&{reply_code}&{reply_name}"

        if args is not None:
            
            if isinstance(args, list):
                args_str = "&".join(args)
            elif isinstance(args, str):
                args_str = args
            elif isinstance(args, int):
                args_str = str(args)
            
            else:
                raise ValueError(
                    f"Unsupported args type {type(args)}"
                )
            
            line += f"&{args_str}"

        line = cls.encrypt(line)

        if len(line.encode('utf-8')) > 64:
            raise ValueError(
                "The callback_data string is too long. It exceeds 64 bytes."
            )

        return line

    @classmethod
    def parse(
        cls, 
        callback: telebot.types.CallbackQuery
    ):
        callback_data = cls.decrypt(callback.data)
        parts = callback_data.split("&")

        reply_code = parts[1]
        reply_type = ReplyTypeConverter.decode(reply_code)

        args = [p for p in parts[3:] if p != ""]  # clear empty parts
        return Callback(
            id=callback.id,
            app_name=parts[0],
            reply_type=reply_type,
            reply_name=parts[2],
            args=args,
        )

    @classmethod
    def encrypt(cls, text: str) -> str:
        # Have to choose encryption method that make not too long strings
        # ... like cryptography.Fernet, coz callback data cannot be bigger 
        # than 64 bytes
        return text

    @classmethod
    def decrypt(cls, token: str) -> str:
        # see cls.encrypt() method comment
        return token


class CallbackInlineRouterBase:
    log = get_logger(__name__)

    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: Callback
    ):
        self.customer = customer
        self.callback = callback

    def is_reply_name(self, name: str) -> bool:
        return self.callback.reply_name == name

    def build_reply(
        self, 
        InlineReply: "replies.CallbackInlineReplyBuilder"
    ):
        builder = InlineReply(self)
        # bot.answer_callback_query(self.callback.id)
        with transaction.atomic():
            builder.build()
        log.debug(
            f"Has been built reply for callback:\n"
            f"{(self.callback.app_name, self.callback.reply_name)}"
        )

    def reply_not_found(self):
        app_name = self.callback.app_name
        reply_name = self.callback.reply_name
        classname = self.__class__.__name__
        raise Exception(
            f"{app_name}:{classname}: "
            f"Reply {reply_name} does not exists"
        )

    def redirect(
        self,
        reply_name: str = None,
        app_name: str = None,
        args: typing.Union[
            str, int, list
        ] = None,
        reply_type: messenger.types.ReplyType = "CALLBACK"
    ):
        if app_name is None:
            app_name = self.callback.app_name

        if reply_name is None:
            raise ValueError(
                "Arg reply_name is required"
            )

        router = self._get_app_router(
            app_name=app_name, 
            reply_type=reply_type,
        )
        if router is None:
            raise Exception(
                f"Cannot find app router by name: {app_name}"
            )

        if not isinstance(args, list):
            args = [args]
        
        if reply_type == "COMMAND":
            return router(
                self.customer,
                reply_name=reply_name 
            ).route()
        elif reply_type == "CALLBACK":
            return router(
                self.customer,
                Callback(
                    id=self.callback.id,
                    app_name=app_name,
                    reply_name=reply_name,
                    args=args,
                    reply_type=reply_type
                )
            ).route()

    def _get_app_router(
        self, 
        reply_type: messenger.types.ReplyType,
        app_name: typing.Optional[str] = None,
    ):
        if app_name is None:
            app_name = self.callback.app_name
        
        try:
            app_module = import_module(f'{app_name}.routers')
        except (ImportError, AttributeError) as e:
            log.exception(
                f"Error loading module or class for app '{app_name}': {e}"
            )
            raise Exception(e)

        if reply_type == "COMMAND":
            router_type = "CommandRouter"
        elif reply_type == "CALLBACK":
            router_type = "CallbackInlineRouter"    
        else:
            raise ValueError(
                f"Unsupported router_type {router_type}"
            )
        return getattr(app_module, router_type) 


class CommandRouterBase:
    
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: typing.Optional[
            telebot.types.Message
        ] = None,
        reply_name: typing.Optional[str] = None,
    ):
        # Проверяем, что хотя бы один из необязательных аргументов задан
        if message is None and reply_name is None:
            raise ValueError("Either 'message' or 'reply_name' must be provided.")

        self.customer = customer
        self.message = message
        self.reply_name = reply_name

        if message is not None:
            self.command = self._parse_command(message)

    def is_reply_name(self, name: str) -> bool:
        return self.reply_name == name

    def build_reply(
        self, 
        InlineReply: "replies.CommandReplyBuilder"
    ):
        builder = InlineReply(self.customer)
        with transaction.atomic():
            builder.build()
        log.debug(
            f"Has been built reply {self.reply_name}:"
        )


class CommandRouter(CommandRouterBase):
    def route(self):
        if self.reply_name is None:
            reply = self._get_reply()
        else:
            import main.replies
            reply = getattr(main.replies, self.reply_name) 
        return reply(
            customer=self.customer,
            message=self.message
        ).build()
        
    def _parse_command(self, message: telebot.types.Message) -> str:
        command = message.text.split()[0][1:]  # Извлечение команды без '/'
        return command

    def _get_reply(self):
        def _is(command: str):
            return self.command == command        
        
        if _is("start"):
            import main.replies  # avoiding circular import 
            return main.replies.StartCommandReply        

        from . import replies
        return replies.CustomCommandReply


class CallbackInlineRouter(CallbackInlineRouterBase):

    def route(self):
        if self.callback.app_name == "custom":
            from . import replies
            return replies.CustomCallbackInlineReply(
                self.customer, self.callback              
            ).build()

        else:
            cb = self.callback
            return self.redirect(
                app_name=cb.app_name,
                reply_name=cb.reply_name,
                args=cb.args
            )


def route_command(
    customer: main.models.Customer, 
    message: telebot.types.Message,
):
    return CommandRouter(
        customer, message 
    ).route()


def route_callback_inline(
    customer: main.models.Customer, 
    callback_query: telebot.types.CallbackQuery
):
    callback = Callback.parse(callback_query)
    return CallbackInlineRouter(
        customer, callback
    ).route()


def build_callback_inline_reply(
    customer: main.models.Customer,
    app_name: str,
    reply_name: str, 
    args: typing.Optional[list] = None
):
    callback = Callback(
        id=1,
        app_name=app_name,
        reply_name=reply_name,
        args=args,
    )

    return CallbackInlineRouter(
        customer, callback
    ).route()

def build_command_reply(
    customer: main.models.Customer,
    reply_name: str, 
):
    return CommandRouter(
        customer=customer,
        reply_name=reply_name
    ).route()
