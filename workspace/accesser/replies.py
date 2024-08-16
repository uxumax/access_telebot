import typing
from datetime import timedelta
from django.utils import timezone
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger
from telebot import TeleBot

# import main.models
from . import models
import cashier.models

from messenger.replies import (
    CallbackInlineReplyBuilder,
    Text,
    translate as _
)


bot = TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


CallbackInlineReply = typing.Union[
    'ChatGroupsReply',
    'GroupSubsReply',
    'MySubsReply',
]


class GroupedSubsReplyBuilder(CallbackInlineReplyBuilder):
    USING_ARGS = (
        'group_id'
    )

    def is_group_id_set(self):
        return self.get_group_id() is not None

    def get_group_id(self) -> int:
        group_id = int(self.callback.args[0]) if self.callback.args else None
        return group_id

    def get_group(self):
        if not hasattr(self, "_group"):
            group_id = self.get_group_id()
            if group_id is None:
                log.info(
                    "Cannot get_group(): group_id does not set to ReplyBuilder"
                )
                return None
            self._group = models.ChatGroup.objects.get(pk=group_id)
        return self._group

    def add_back_button(self):
        group = self.get_group()
        if group is None:
            return
        self.add_button(
            _("Back"),
            reply_name="ChatGroupsReply",
            args=group.parent_group_id
        )

    def add_cancel_button(self):
        self.add_button(
            _("Cancel"),
            app_name="main",
            reply_name="StartReply"
        )


class ChatGroupsReply(GroupedSubsReplyBuilder):
    USING_ARGS = (
        'group_id'
    )

    def build(self):
        if self.is_group_id_set():
            if self._has_child_groups():
                self._add_child_groups_buttons()
                self.add_back_button()
            else:
                return self.router.redirect(
                    "GroupSubsReply",
                    args=self.get_group_id()
                )
        else:
            self._add_top_groups_buttons()

        self.add_cancel_button()

        text = _(
            "Choose chat group: "
        )

        self.send_message(
            text,
            reply_markup=self.markup
        )  

    def _has_child_groups(self):
        group = self.get_group()
        return group.child_groups.exists()

    def _add_group_buttons(self, groups):
        for group in groups:
            self.add_button(
                group.name,
                reply_name="ChatGroupsReply",
                args=group.id
            )

    def _add_top_groups_buttons(self):
        groups = self._get_top_groups()
        self._add_group_buttons(groups)

    def _add_child_groups_buttons(self):
        groups = self._get_child_groups()
        self._add_group_buttons(groups)

    def _get_child_groups(self) -> list:
        group_id = self.get_group_id()
        parent_group = models.ChatGroup.objects.get(pk=group_id)
        groups = [group for group in parent_group.child_groups.all()]
        return groups

    def _get_top_groups(self) -> list:
        groups = []
        groups_with_sub = models.ChatGroup.objects.with_subscription().all()
        for group_ws in groups_with_sub:

            if group_ws.parent_group:
                group = group_ws.get_top_parent()
            else:
                group = group_ws

            if group not in groups:
                groups.append(group)

        return groups


class GroupSubsReply(GroupedSubsReplyBuilder):
    USING_ARGS = (
        'group_id'
    )

    def build(self):
        subs: typing.List[models.Subscription] = self._get_subscriptions()
        if not subs:
            text = _(
                "Do not have any subscriptions for this group"
            )
            return self.router.redirect(
                app_name="main",
                reply_name="StartCommandReply",
                reply_type="COMMAND"
            )

        text = _(
            "Choose subscription: "
        )

        self.send_message(
            text,
            reply_markup=self._build_markup(subs)
        )  

    def _get_subscriptions(self) -> list:
        group = self.get_group()
        subs = group._get_subscriptions()
        return subs

    def _build_markup(self, subs: typing.List[models.Subscription]):
        # for sub in accesser.models.Subscription.objects.all():
        for sub in subs:
            self.add_button(
                sub.name,
                "cashier", "ChooseAccessDurationReply",
                args=sub.id
            )

        self.add_back_button()
        self.add_cancel_button()
        return self.markup


class MySubsReply(CallbackInlineReplyBuilder):
    def build(self):
        self.customer_chat_accesses = models.CustomerChatAccess.objects.filter(
            customer=self.customer
        ).all()
        
        if self.customer_chat_accesses:
            text = self._get_text()
        else:
            text = _(
                "Sorry, you don't have an active plan right now"
            )

        self.send_message(
            text,
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        # payments buttons

        return None  # self.markup
 
    def _get_text(self):
        text = _(
            "You have these subscriptions: \n"
            "{{subs_list}}"
        ).context(
            subs_list=self._get_subscription_list_str()
        )
        text += "\n\n"
        text += _(
            "You have access to chat/channels: \n"
            "{{access_list}}"
        ).context(
            access_list=self._get_customer_access_chat_list_str()
        )
        return text

    def _get_subscription_list_str(self) -> str:
        text = Text("")
        for subs in self._get_subscription_list():
            text += _(
                "{{subs_name}}\n"
            ).context(
                subs_name=subs.name
            )
        return text.load()

    def _get_subscription_list(self) -> list:
        subs_list = []
        for access in self.customer_chat_accesses:
            if access.subscription not in subs_list:
                subs_list.append(access.subscription)
        return subs_list

    def _get_customer_access_chat_list_str(self) -> str:
        text = Text("")
        unique_chats = []
        for access in self.customer_chat_accesses:
            for chat in access.chat_group.get_all_child_chats():
                # Clear all dublicates from two different sub with same chats
                if chat not in unique_chats:
                    invite_link = access.invite_links.filter(chat=chat).first()
                    unique_chats.append(
                        (
                            chat,
                            # invite_link.url if invite_link is not None else None,
                            getattr(invite_link, "url", None),
                            access.end_date,
                        )
                    )

        for chat, invite_link, end_date in unique_chats:
            text += _(
                "{{chat_title}}\n"
                "{{invite_link}}\n"
                "Until {{date}}\n"
                "--------"
            ).context(
                chat_title=chat.title,
                invite_link=invite_link,
                date=end_date
            )
            text += "\n"
        return text.load() 


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
                    "Can't send invite links because can't find your confirmed invoice"       
                )
            )

        customer_chat_accesses = self._assign_subscription_access(
            invoice.subscription, 
            invoice.duration.duration,        
        )
        
        invite_links = self._get_invite_links(customer_chat_accesses)
        invite_links_text = self._get_invite_links_str(invite_links)
        self.send_message(
            _(
                "Here are your invite links:\n"
                "{{link_list}}"
            ).context(
                link_list=invite_links_text
            )
        )

        valid_until_date = (
            timezone.now() + invoice.duration.duration
        ).strftime("%B %d, %Y %H:%M")
        self.send_message(
            _(
                "All invite links will be valid until {{date}}"
            ).context(
                date=valid_until_date
            )
        )

        invoice.status = "REDEEMED"
        invoice.save()
        
        return self.router.redirect(
            "MySubsReply"
        )

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
        for access in subscription.access_to_chat_group.all():
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
                    access, chat
                ) 
                links.append(
                    (chat.title, link)
                )
        return links

    def _create_invite_link(
        self, 
        access: models.CustomerChatAccess,
        chat: models.Chat, 
    ) -> str: 
        expire_timestamp = int(access.end_date.timestamp())
        link_name = self._get_invite_link_name(chat.chat_id)
        try:    
            invite_link = bot.create_chat_invite_link(
                name=link_name,
                chat_id=chat.chat_id,  
                expire_date=expire_timestamp,  # Expiration date as a Unix timestamp
                member_limit=1,
                creates_join_request=False  # This will require administrators to approve join requests
            )
        except Exception as e:
            log.exception(e)
            raise Exception(
                "Cannot make invite link for {self.customer} "
                f"to chat {chat.chat_id}:\n {e}"
            )
        
        invite_link_str = invite_link.invite_link

        models.InviteLink.objects.create(
            name=link_name,
            url=invite_link_str,
            customer=self.customer,
            chat=chat,
            access=access,
            expire_date=access.end_date
        )

        return invite_link_str

    def _get_invite_link_name(self, chat_id: int):
        time = timezone.now().timestamp()  # for uniqilize link name
        return (
            f"{self.customer.chat_id}:{chat_id}:{time}"
        )

    def _get_invite_links_str(
        self, 
        links: typing.List[
            typing.Tuple[str, str]
        ]
    ) -> str:
        text = Text("")
        for chat_title, link in links:
            text += _(
                "-- {{chat_title}} - {{link}}\n"
            ).context(
                chat_title=chat_title,
                link=link
            )
        return text.load()


class RevokeAccessNotificationReply(CallbackInlineReplyBuilder):
    USING_ARGS = (
        "revoked_access_id",
    )

    def build(self):
        revoked_access = self._get_revoked_access()
        revoked_chats_list_text = self._get_revoked_chat_list_str(
            revoked_access
        )

        self.send_message(
            _(
                "Your access to these channels has been revoked:\n"
                "{{chat_list}}",
            ).context(
                chat_list=revoked_chats_list_text
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

    def _get_revoked_chat_list_str(
        self, 
        revoked_access: models.CustomerChatAccess
    ) -> str:
        text = Text("")
        for chat in revoked_access.chat_group.chats.all():
            row: Text = _(
                "-- {{chat_title}}\n"
            ).context(
                chat_title=chat.title
            )
            text += row
        return row.load()
    
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

