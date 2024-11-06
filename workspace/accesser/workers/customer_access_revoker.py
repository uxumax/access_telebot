from django.utils import timezone
from django.db.models import Q
from access_telebot.logger import get_logger
import telebot
import time

from main.workers import core
import messenger.models
from messenger.routers import build_callback_inline_reply
from accesser import models

from access_telebot.settings import (
    TELEBOT_KEY,
    NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE,
    WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS,
)

bot = telebot.TeleBot(TELEBOT_KEY)
log = get_logger(__name__)


class Worker(core.Worker):
    beat_interval = 60 * 5 
    stat = models.CustomerAccessRevokerWorkerStat

    def start(self):
        while not self.stop_event.is_set():
            try:
                self._beat()
                self.wait()
            except Exception as e:
                log.exception(e)
                break

        log.warning(f"Worker:{__name__} has been stopped")
        return

    def _beat(self):
        self._refresh_expiring_range()

        # Add notifications of expiring
        for access in self._get_expiring_accesses():
            if self._already_has_expiring_notification(access):
                continue
            self._add_expiring_notification(access)

        # Revoke accesses
        for access in self._get_accesses_for_revoke():
            self._revoke_access(access)
            log.info(
                f"Access {access} has been revoked in Telegram API"
            )
            self._set_inactive(access)
            self._notify_customer_about_revoking(access)

    def _refresh_expiring_range(self):
        self.now = timezone.now()
        # Set static range for whole beat
        self.start_expiring_date = (
            self.now + NOTIFIER_SUBSCRIBTION_EXPIRRING_DAYS_BEFORE
        )
        self.revoke_date = (
            self.now - WAIT_AFTER_SUBSCRIBTION_EXPIRED_DAYS
        )

    def _get_expiring_accesses(self):
        # Get expiring accesses but not for revoke
        return models.CustomerChatAccess.objects.filter(
            active=True,
            end_date__lte=self.start_expiring_date,
            end_date__gt=self.revoke_date,
        ).all()

    def _get_accesses_for_revoke(self):
        return models.CustomerChatAccess.objects.filter(
            active=True,
        ).filter(
            Q(
                revoking_method="GENTLE",
                end_date__lte=self.revoke_date,
            ) | Q(
                revoking_method="FORCE",
                end_date__lte=timezone.now(),
            ) | Q(
                # Revoke trial accesses forcly too
                is_trial=True, 
                end_date__lte=timezone.now(),
            )
        ).all()

    @staticmethod
    def _revoke_access(access):
        for chat in access.subscription.get_all_child_chats():
            try:
                bot.ban_chat_member(
                    chat.chat_id, access.customer.chat_id
                )
                access.revoke_date = timezone.now()
                access.save()
                log.info(
                    f"Access to chat {chat} has been revoked "
                    f"for customer {access.customer}"
                )
                time.sleep(0.5)
            except telebot.apihelper.ApiTelegramException as e:
                if "USER_NOT_PARTICIPANT" in str(e):
                    log.warning(
                        f"Cannot revoke access to chat: {chat} "
                        f"coz customer {access.customer} is not participant"
                    )

    @staticmethod
    def _set_inactive(access):
        access.active = False
        access.save()

    @staticmethod
    def _notify_customer_about_revoking(access):
        # Notify right now
        return build_callback_inline_reply(
            customer=access.customer,
            app_name="accesser",
            reply_name="RevokeAccessNotificationReply",
            args=[access.id]
        )

    @staticmethod
    def _add_expiring_notification(access):
        messenger.models.Notification.objects.create(
            customer=access.customer,
            app_name="accesser",
            reply_name="SubscriptionExpiringNotificationReply",
            args=access.id,
            alert_date=timezone.now(),  # show now
        )

    @staticmethod
    def _already_has_expiring_notification(access):
        # Check customer already have one at least expiring 
        # access notification
        return messenger.models.Notification.objects.filter(
            customer=access.customer,
            app_name="accesser",
            reply_name="SubscriptionExpiringNotificationReply",
            is_sent=False,
        ).exists()
