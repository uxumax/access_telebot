import typing
from datetime import timedelta
from django.utils import timezone
from access_telebot.settings import (
    TELEBOT_KEY,
    NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE,
    WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS,
)
from access_telebot.logger import get_logger
from telebot import TeleBot
from django.db.models import Q

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
    'ChooseSubscriptionReply',
    'MySubscriptionsReply',
]


class SubscriptionReplyBuilder(CallbackInlineReplyBuilder):
    USING_ARGS = (
        'subscription_id'
    )

    def is_subscription_id_set(self):
        return self.get_subscription_id() is not None

    def get_subscription_id(self) -> int:
        subscription_id = int(self.callback.args[0]) if self.callback.args else None
        return subscription_id

    def get_subscription(self):
        if not hasattr(self, "_subscription"):
            subscription_id = self.get_subscription_id()
            if subscription_id is None:
                log.debug(
                    "Cannot get_subscription(): subscription_id does not set to ReplyBuilder"
                )
                return None
            self._subscription = models.Subscription.objects.get(pk=subscription_id)
        return self._subscription

    def add_back_button(self):
        subscription = self.get_subscription()
        if subscription is None:
            return
        if subscription.parent is None:
            args = None  # Show top subscriptions
        elif subscription.parent.is_whole_only:
            args = None  # Show top subscriptions
        else:
            args = subscription.parent_id

        self.add_button(
            _("Back"),
            reply_name="ChooseSubscriptionReply",
            args=args
        )

    def add_cancel_button(self):
        self.add_button(
            _("Cancel"),
            app_name="main",
            reply_name="StartReply"
        )


class ChooseSubscriptionReply(SubscriptionReplyBuilder):
    USING_ARGS = (
        'subscription_id'
    )

    def build(self):
        if self.is_subscription_id_set():
            subscription = self.get_subscription()
            if subscription.childs.exists() and not subscription.is_whole_only:
                self._add_subscriptions_buttons(subscription.childs.all())
                self._add_all_childs_button(subscription)
                self.add_back_button()
            else:
                return self.router.redirect(
                    app_name="cashier", 
                    reply_name="ChooseAccessDurationReply",
                    args=subscription.id
                )
        else:
            self._add_top_subscriptions_buttons()

        self.add_cancel_button()

        text = _(
            "Choose chat subscription: "
        )

        self.send_message(
            text,
            reply_markup=self.markup
        )  

    def _add_subscriptions_buttons(self, subscriptions):
        for sub in subscriptions:
            self.add_button(
                sub.name,
                reply_name="ChooseSubscriptionReply",
                args=sub.id
            )

    def _add_all_childs_button(self, subscription):
        self.add_button(
            _("Choose all"),
            app_name="cashier",
            reply_name="ChooseAccessDurationReply",
            args=subscription.id
        )

    def _add_top_subscriptions_buttons(self):
        subscriptions = self._get_top_subscriptions()
        self._add_subscriptions_buttons(subscriptions)

    def _get_top_subscriptions(self) -> list:
        top_subs = []
        subscriptions = models.Subscription.objects.filter(
            Q(
                parent_id__isnull=True
            ) | Q(
                is_top=True
            )
        ).all()

        for sub in subscriptions:
            if sub.parent and not sub.is_top:
                top_sub = sub.get_top_parent()
            else:
                top_sub = sub 
            if top_sub not in top_subs:
                top_subs.append(top_sub)

        return top_subs


class MySubscriptionsReply(CallbackInlineReplyBuilder):
    def build(self):
        self.customer_chat_accesses = models.CustomerChatAccess.objects.filter(
            customer=self.customer
        ).all()
        
        if not self.customer_chat_accesses:
            self.send_message(
                _(
                    "Sorry, you don't have an active plan right now"
                )
            )
            return

        self.send_message(
            _(
                "You have these subscriptions: \n"
                "{{subs_list}}"
            ).context(
                subs_list=self._get_subscription_list_str()
            ),
            reply_markup=self._build_markup()
        )  

    def _build_markup(self):
        self.add_button(
            _("Get invite links"),
            reply_name="RemindInviteLinksReply"
        )
        self.add_button(
            _("Back"),
            app_name="main",
            reply_name="StartReply"
        )
        return self.markup
 
    def _get_subscription_list_str(self) -> str:
        text = Text("")
        # for subs in self._get_subscription_list():
        for access in self.customer_chat_accesses:
            text += _(
                "{{subs_name}}\n"
                "Access to {{chat_count}} channel/chats\n"
                "{{start_date}} | {{end_date}}\n\n"
            ).context(
                subs_name=access.subscription.name,
                chat_count=access.subscription.get_all_child_chats().count(),
                start_date=access.start_date.strftime("%d-%m-%Y %H:%M"),
                end_date=access.end_date.strftime("%d-%m-%Y %H:%M")
            )
        return text.load()


class InviteLinkSendReplyBuilder(CallbackInlineReplyBuilder):
    def send_invite_links(
        self, 
        links: typing.List[
            typing.Tuple[str, str]
        ]
    ):
        text = Text("")
        for i, (chat_title, link) in enumerate(links):
            text += _(
                "-- {{chat_title}} - {{link}}\n"
            ).context(
                chat_title=chat_title,
                link=link
            )

            # Send links no more than 10 pcs in a message
            if (i + 1) % 10 == 0 or i == len(links) - 1:
                self.send_message(
                    text.load()
                )
                text = Text("")  # Reset text for the next batch


class InvoiceFinderReplyBuilder(CallbackInlineReplyBuilder):
    USING_ARGS = (
        "invoice_type_code",
        "confirmed_invoice_id",
    )

    def get_invoice(self):
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
            return self.router.redirect(
                app_name="main",
                reply_name="StartReply"
            )
            # raise Exception(
            #     f"Cannot find confirmed invoice with id {invoice_id}"
            # )

    def _get_invoice_type_code(self) -> str:
        return self.callback.args[0]

    def _get_confirmed_invoice_id(self) -> int:
        return int(self.callback.args[1])


class SubscriptionRechargedReply(InvoiceFinderReplyBuilder):
    USING_ARGS = (
        "invoice_type_code",
        "confirmed_invoice_id",
    )

    def build(self):
        invoice = self.get_invoice()
        self._prolongate_access(
            invoice.access,
            invoice.duration.duration
        )
        invoice.status = "REDEEMED"
        invoice.save()

        text = _(
            "Your subscription {{subscription_name}} has been rechrged"
            "and will be end {{end_date}}"
        ).context(
            subscription_name=invoice.access.subscription.name,
            end_date=invoice.access.end_date.strftime("%d-%m-%Y %H:%M")
        )
        self.send_message(
            text
        )
        self.router.redirect(
            app_name="main",
            reply_name="StartReply"
        )
    
    @staticmethod
    def _prolongate_access(
        access: models.CustomerChatAccess,
        duration: timedelta
    ):
        if access.revoked_date is None:
            # Access was not revoked
            access.end_date += duration
        else:
            # Access was revoked
            access.end_date = (
                access.revoked_date + duration
            ) - WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS
        access.active = True 
        access.save()


class GiveInviteLinksReply(
    InviteLinkSendReplyBuilder,
    InvoiceFinderReplyBuilder
):
    USING_ARGS = (
        "invoice_type_code",
        "confirmed_invoice_id",
    )

    def build(self):
        invoice = self.get_invoice()
        customer_chat_access = self._assign_subscription_access(
            invoice.subscription, 
            invoice.duration.duration,        
        )
        
        invite_links = self._get_invite_links(customer_chat_access)
        self.send_message(
            "Here is your invite links"
        )
        self.send_invite_links(invite_links)

        valid_until_date = (
            timezone.now() + invoice.duration.duration
        ).strftime("%d-%m-%Y %H:%M")
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
            "MySubscriptionsReply"
        )

    def _assign_subscription_access(
        self,
        subscription: models.Subscription,
        duration: timedelta,
    ) -> None:
        start_date = timezone.now()
        end_date = start_date + duration
        access = models.CustomerChatAccess.objects.create(
            customer=self.customer,
            start_date=start_date,
            end_date=end_date,
            subscription=subscription,
            active=True,
        )
        return access

    def _get_invite_links(
        self,
        access: models.CustomerChatAccess,
    ) -> list:
        links = []
        # for chat in access.subscription.chats.all():
        for chat in access.subscription.get_all_child_chats():
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
        # expire_timestamp = int(access.end_date.timestamp())
        link_name = self._get_invite_link_name(chat.chat_id)
        try:    
            invite_link = bot.create_chat_invite_link(
                name=link_name,
                chat_id=chat.chat_id,  
                # expire_date=expire_timestamp,  # Expiration date as a Unix timestamp
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

    # def _get_invite_links_str(
    #     self, 
    #     links: typing.List[
    #         typing.Tuple[str, str]
    #     ]
    # ) -> str:
    #     text = Text("")
    #     for chat_title, link in links:
    #         text += _(
    #             "-- {{chat_title}} - {{link}}\n"
    #         ).context(
    #             chat_title=chat_title,
    #             link=link
    #         )
    #     return text.load()


class RemindInviteLinksReply(InviteLinkSendReplyBuilder):
    USING_ARGS = ()

    def build(self):
        self.customer_chat_accesses = models.CustomerChatAccess.objects.filter(
            customer=self.customer
        ).all()
        
        if not self.customer_chat_accesses:
            self.send_message(
                _(
                    "Sorry, you don't have an active plan right now"
                )
            )
            return

        invite_links = self._get_invite_links()
        self.send_invite_links(invite_links)
        self.send_message(
            "All links will be deactivated when subscription become expired",
            reply_markup=self._build_markup()
        )

    def _get_invite_links(self) -> list:
        unique_chats = []
        for access in self.customer_chat_accesses:
            for chat in access.subscription.get_all_child_chats():
                # Clear all dublicates from two different sub with same chats
                if chat not in unique_chats:
                    invite_link = access.invite_links.filter(chat=chat).first()
                    unique_chats.append(
                        (
                            chat.title,
                            getattr(invite_link, "url", None),
                        )
                    )
        return unique_chats

    def _build_markup(self):
        self.add_button(
            _("Back"),
            app_name="main",
            reply_name="StartReply"
        )
        return self.markup


class SubscriptionExpireNotificationBuilder(CallbackInlineReplyBuilder):
    USING_ARGS = (
        "access_id",
    )

    def get_access(self):
        access_id = self._get_access_id()
        return models.CustomerChatAccess.objects.get(
            pk=access_id,
            # active=False
        )

    def _get_access_id(self):
        return int(self.callback.args[0])

    def get_customer_expiring_accesses(self):
        access = self.get_access()
        customer = access.customer
        return models.CustomerChatAccess.objects.filter(
            customer=customer,
            end_date__lt=timezone.now() + NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE  # timedelta  from LOCAL_SETTING
        )


class SubscriptionExpiringNotificationReply(SubscriptionExpireNotificationBuilder):
    USING_ARGS = (
        "access_id",
    )

    def build(self):
        text = _("Please do not forget recharge your subscription(s):\n") 
        accesses = self.get_customer_expiring_accesses()
        if accesses.count() == 0:
            self.send_message(
                _("You don't have any expiring subscription")
            )
            return self.router.redirect(
                app_name="main",
                reply_name="StartReply"
            )

        for access in accesses:
            context = {
                "subscription_name": access.subscription.name,
                "expire_date": access.end_date
            }
            if access.end_date < timezone.now():
                text += _(
                    "{{subscription_name}}\nWill be expired {{expire_date}}\n"
                ).context(**context)
            else:
                text += _(
                    "{{subscription_name}}\nAlready expired {{expire_date}}\n"
                ).context(**context)
            text += "\n"

        self.send_message(
            text,
            reply_markup=self._build_markup(accesses)
        )

    def _build_markup(self, accesses):
        for access in accesses:
            text = _(
                "Recharge {{subscription_name}}"
            ).context(
                subscription_name=access.subscription.name
            )
            self.add_button(
                text,
                app_name="cashier",
                reply_name="RechargeSubscriptionReply",  
                args=access.id
            )
        return self.markup
            

class RevokeAccessNotificationReply(SubscriptionExpireNotificationBuilder):
    USING_ARGS = (
        "access_id",
    )

    def build(self):
        revoked_access = self.get_access()
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

    def _get_revoked_chat_list_str(
        self, 
        revoked_access: models.CustomerChatAccess
    ) -> str:
        text = Text("")
        for chat in revoked_access.subscription.get_all_child_chats():
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
        self.add_button(
            _("Restore access"),
            app_name="cashier",
            reply_name="RechargeSubscriptionReply",  # TODO
            args=revoked_access.id
        )
        return self.markup

