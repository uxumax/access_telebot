import typing
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
import telebot
import main.models
import accesser.models
from messenger.replies import CallbackInlineReplyBuilderBase
from . import models


bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


CallbackInlineReply = typing.Union[
    'InlineReplyMySubs',
    'InlineReplyAllSubs',
]


class InlineReplyAllSubs(CallbackInlineReplyBuilderBase):
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


class InlineReplyMySubs(CallbackInlineReplyBuilderBase):
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


# class TronInvoiceBuildRouter:
#     def __init__(
#         self,
#         # customer: main.models.Customer
#     ):
#         pass
#         # self.customer = customer

#     def build(
#         self,
#         customer,
#         subscription,
#         network,
#         amount,

#     ) -> models.CryptoInvoice:
#         address = self._get_free_address()
#         if address is None:
#             address = self._create_new_address()

#         invoice = models.CryptoInvoice.objects.create(
#             customer=customer,
#             subscription=subscription,

#         )
#         return invoice

#     @staticmethod
#     def _get_free_address():
#         return models.TronAddress.objects.filter(
#             status=models.TronAddressStatusChoices.FREE
#         ).first()

#     @staticmethod
#     def _create_new_address() -> models.TronAddress:
#         address, private_key = tron_wallet.create_tron_account()
#         address = models.TronAddress.objects.create(
#             address=address,
#             private_key=private_key,
#             status=models.TronAddressStatusChoices.BUSY
#         )
#         return address