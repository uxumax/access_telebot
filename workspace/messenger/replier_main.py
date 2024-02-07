from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
import telebot
import typing 

import main.models
import accesser.models
import messenger.models


log = get_logger(__name__)
bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)

CommandReply = typing.Union[
    'CommandReplyStart',
]


CallbackInlineReply = typing.Union[
    'InlineReplyMySubs',
    'InlineReplyAllSubs',
]


class BaseCommandReplyBuilder:
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message,
    ):
        self.customer = customer
        self.message = message


class BaseCallbackInlineReplyBuilder:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback


class InlineReplyAllSubs(BaseCallbackInlineReplyBuilder):
    def build(self):
        text = (
            "Our plans: "
        )

        bot.send_message(
            self.customer.chat_id,
            text,
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        markup = telebot.types.InlineKeyboardMarkup()

        for sub in accesser.models.Subscription.objects.all():
            markup.add(
                telebot.types.InlineKeyboardButton(
                    sub.name, callback_data=sub.slug
                )
            )

        return markup


class InlineReplyMySubs(BaseCallbackInlineReplyBuilder):
    def build(self):
        self.customer_chat_accesses = accesser.models.CustomerChatAccess.objects.filter(
            customer=self.customer
        ).all()
        
        if self.customer_chat_accesses:
            text = self._get_text()
        else:
            text = (
                "Sorry, you don't have active plan right now"
            )

        bot.send_message(
            self.customer.chat_id,
            text,
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton

        # payments buttons

        return markup

    def _get_text(self):
        text = (
            "You have these subscriptions: \n"
            f"{self._get_subscription_list_text()}"
            "\n"
        )
        text += (
            "You have access to chat/channels: \n"
            f"{self._get_customer_access_chat_list_text()}"
            "\n"            
        )
        return text

    def _get_subscription_list_text(self):
        text = ""
        for subs in self._get_subscription_list():
            text += f"{subs.name}\n"
        return text

    def _get_subscription_list(self):
        subs_list = []
        for access in self.customer_chat_accesses:
            if access.subscription not in subs_list:
                subs_list.append(access.subscription)
        return subs_list

    def _get_customer_access_chat_list_text(self):
        text = ""
        unique_chats = []
        for access in self.customer_chat_accesses:
            for chat in access.chat_group.get_all_child_chats():
                # Clear all dublicates from two different sub with same chats
                if chat not in unique_chats:
                    unique_chats.append(chat)

        for chat in unique_chats:
            text += f"{chat.title} до {access.end_date}\n"

        return text  


class CommandReplyStart(BaseCommandReplyBuilder):
    def build(self):
        text = (
            "Hi. I am your accessbot"
        )

        bot.reply_to(
            self.message,
            text,
            reply_markup=self._build_markup()
        )        

    def _build_markup(self):
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton

        markup.add(
            button(
                "Plans", callback_data="all_subs"
            )
        )

        markup.add(
            button(
                "My plan", callback_data="my_subs"
            )
        )

        markup.add(
            button(
                "Contact", callback_data="raw_contact"
            )
        )

        return markup


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
        def _is(command: str):
            return self.command == command        
        
        if _is("start"):
            return CommandReplyStart(*self.build_args).build()


class CallbackInlineRouter:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery,
    ):
        self.customer = customer
        self.callback = callback

    def route(self):
        def _is(data: str):
            return self.callback.data == data        
        
        if _is("my_subs"):
            return self._build_reply(InlineReplyMySubs)

        if _is("all_subs"):
            return self._build_reply(InlineReplyAllSubs)

        bot.answer_callback_query(
            self.callback.id, 
            f"I don't know callback {self.callback.data}"
        )

    def _build_reply(
        self, 
        InlineReply: CallbackInlineReply
    ):
        bot.answer_callback_query(self.callback.id)
        return InlineReply(
            self.customer, self.callback
        ).build()


# class CallbackInlineReply(BaseCallbackInlineReplyBuilder):
#     def __init__(
#         self, 
#         customer: main.models.Customer, 
#         callback: telebot.types.CallbackQuery
#     ):
#         self.customer = customer
#         self.callback = callback

#     def build(self):
#         try:
#             reply = messenger.models.CallbackInlineReply.objects.get(
#                 callback_data=self.callback.data
#             )
#         except main.models.CallbackInlineReply.DoesNotExist:  # Исправлена опечатка здесь
#             bot.answer_callback_query(  # Используйте этот метод для отправки уведомления пользователю
#                 self.callback.id, 
#                 f"I don't know callback {self.callback.data}"
#             )
#             return

#         # Используйте этот метод, чтобы сказать телеге, что сигнал от кнопки получен
#         bot.answer_callback_query(self.callback.id)
        
#         # Используйте send_message для ответа в чат, а не reply_to
#         bot.send_message(
#             self.callback.message.chat.id,  # Получаем ID чата из callback.message
#             reply.text,
#             reply_markup=self.build_markup(reply)
#         )



