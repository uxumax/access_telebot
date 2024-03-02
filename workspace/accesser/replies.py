import typing
from datetime import datetime, timedelta
from django.utils import timezone
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
from telebot import TeleBot

import main.models
import accesser.models
import cashier.models
from . import models

from messenger.replies import (
    CallbackInlineReplyBuilder,
    translate as _
)

        



bot = TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


CallbackInlineReply = typing.Union[
    'AllSubsReply',
    'MySubsReply',
]


class AllSubsReply(CallbackInlineReplyBuilder):
    def build(self):
        text = _(
            "Our plans: "
        )

        bot.send_message(
            self.customer.chat_id,
            text,
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        for sub in accesser.models.Subscription.objects.all():
            self.add_button(
                sub.name,
                "cashier", "ChooseAccessDurationReply",
                args=sub.id
            )

        return self.markup


class MySubsReply(CallbackInlineReplyBuilder):
    def build(self):
        self.customer_chat_accesses = accesser.models.CustomerChatAccess.objects.filter(
            customer=self.customer
        ).all()
        
        if self.customer_chat_accesses:
            text = self._get_text()
        else:
            text = _(
                "Sorry, you don't have active plan right now"
            )

        bot.send_message(
            self.customer.chat_id,
            text,
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        # payments buttons

        return None  # self.markup
 
    def _get_text(self):
        text = _(
            (
                "You have these subscriptions: \n"
                "{{subs_list}}"
                "\n"
            ),
            {
                "subs_list": self._get_subscription_list_text()
            }
        )
        text += _(
            (
                "You have access to chat/channels: \n"
                f"{{access_list}}"
                "\n"            
            ),
            {
                "access_list": self._get_customer_access_chat_list_text()
            }
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


class GiveInviteLinksReply(CallbackInlineReplyBuilder):
    USING_ARGS = (
        "invoice_type_code",
        "confirmed_invoice_id",
    )

    def build(self):
        invoice = self._get_invoice()
        if invoice.status != "CONFIRMED":
            self.send_message(
                _(
                   "Cannot give give keys coz connot find your confirmed invoice"       
                )
            )

        customer_chat_accesses = self._assign_subscription_access(
            invoice.subscription, 
            invoice.duration.duration,        
        )
        
        invite_links = self._get_invite_links(customer_chat_accesses)
        invite_links_text = self._get_invite_links_text(invite_links)
        self.send_message(
            text=_(
                (
                    "Here are your invite links:\n"
                    "{{link_list}}"
                ),
                {
                    "link_list": invite_links_text
                }
            )
        )

        valid_until_date = (
            timezone.now() + invoice.duration.duration
        ).strftime("%B %d, %Y %H:%M")
        self.send_message(
            _(
                ("All invite links will be valid until {{date}}"),
                {
                    "date": valid_until_date
                }
            )
        )

        invoice.status = "REDEEMED"
        invoice.save()

    def _get_invoice(self):
        invoice_type_code = self._get_invoice_type_code()
        invoice_id = self._get_confirmed_invoice_id()
        if invoice_type_code == "c":  # crypto invoices
            return self._get_crypto_invoice(invoice_id)
        else:
            raise ValueError(
                f"Unsupported invoice type code {invoice_type_code}"
            )
    
    def _get_crypto_invoice(
        self,
        invoice_id: int
    ):
        try:
            return cashier.models.CryptoInvoice.objects.select_related(
                'subscription', 
                'duration',
                'customer',
            ).get(
                id=invoice_id, 
                customer=self.customer,
                status="CONFIRMED",
            )
        except cashier.models.CryptoInvoice.DoesNotExist:
            self.send_message(
                _("Cannot find your invoice")
            )
            raise Exception(
                f"Cannot find confirmed invoice with id {invoice_id}"
            )

    def _get_invoice_type_code(self) -> str:
        return self.callback.args[0]

    def _get_confirmed_invoice_id(self) -> int:
        return int(self.callback.args[1])

    def _assign_subscription_access(
        self,
        subscription: models.Subscription,
        duration: timedelta,
    ) -> None:
        start_date = timezone.now()
        end_date = start_date + duration
        accesses = []
        for access in subscription.access_to_chat_groups.all():
            access = models.CustomerChatAccess.objects.create(
                customer=self.customer,
                chat_group=access.chat_group,
                start_date=start_date,
                end_date=end_date,
                subscription=subscription,
                active=True,
            )
            accesses.append(access)
        return accesses

    def _get_invite_links(
        self,
        customer_chat_accesses: typing.List[
            models.CustomerChatAccess,
        ]
    ) -> list:
        links = []
        for access in customer_chat_accesses:
            for chat in access.chat_group.chats.all():
                link = self._create_invite_link(
                    chat.chat_id, access.end_date
                ) 
                links.append(
                    (chat.title, link)
                )
        return links

    def _create_invite_link(self, chat_id: int, end_date: datetime) -> str: 
        expire_timestamp = int(end_date.timestamp())
        link_name = self._get_invite_link_name(chat_id)
        try:    
            invite_link = bot.create_chat_invite_link(
                name=link_name,
                chat_id=chat_id,  
                expire_date=expire_timestamp,           # Expiration date as a Unix timestamp
                member_limit=1,
                creates_join_request=False               # This will require administrators to approve join requests
            )
        except Exception as e:
            log.exception(e)
        return invite_link.invite_link

    def _get_invite_link_name(self, chat_id: int):
        time = timezone.now().timestamp()  # for uniqilize link name
        return (
            "{self.customer.chat_id}:{chat_id}:{time}"
        )

    def _get_invite_links_text(
        self, 
        links: typing.List[
            typing.Tuple[str, str]
        ]
    ):
        text = ""
        for chat_title, link in links:
            text += f"-- {chat_title} - {link}\n"
        return text


class RevokeAccessNotificationReply(CallbackInlineReplyBuilder):
    USING_ARGS = (
        "revoked_access_id",
    )

    def build(self):
        revoked_access = self._get_revoked_access()
        revoked_chats_list_text = self._get_revoked_chat_list_text(
            revoked_access
        )

        self.send_message(
            _(
                (
                    "Your access to these channels has been revoked:\n"
                    "{{chat_list}}",
                ),
                {
                    "chat_list": revoked_chats_list_text
                }
            ),
            reply_markup=self._build_markup(revoked_access)
        )

    def _get_revoked_access(self):
        access_id = self._get_revoked_access_id()
        return models.CustomerChatAccess.objects.get(
            pk=access_id,
            active=False
        )

    def _get_revoked_access_id(self):
        return self.callback.args[0]

    def _get_revoked_chat_list_text(
        self, 
        revoked_access: models.CustomerChatAccess
    ):
        text = ""
        for chat in revoked_access.chat_group.chats.all():
            row = f"-- {chat.title}\n"
            text += row
        return row
    
    def _build_markup(
        self,
        revoked_access: models.CustomerChatAccess
    ):
        if revoked_access.subscription is not None:
            self.add_button(
                _("Buy access again"),
                app_name="cashier",
                reply_name="ChooseAccessDurationReply",
                args=revoked_access.subscription.id
            )
        return self.markup

