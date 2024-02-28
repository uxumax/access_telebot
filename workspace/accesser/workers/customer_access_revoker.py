from django.utils import timezone
from access_telebot.logger import get_logger
import telebot
from time import sleep

from main.workers import core
from accesser import models
from access_telebot.settings import (
    TELEBOT_KEY,
)

bot = telebot.TeleBot(TELEBOT_KEY)
log = get_logger(__name__)


class Worker(core.Worker):
    beat_interval = 60 * 5 
    stat = models.CustomerAccessRevokerWorkerStat

    def start(self):
        while not self.stop_event.is_set():
            self._beat()
            self.wait()

    def _beat(self):
        for access in self._get_all_expired_accesses():
            self._revoke_access(access)
            log.info(
                f"Access {access} has been revoked in Telegram API"
            )
            self._set_inactive(access)
            self._notify_customer(access)

    @staticmethod
    def _get_all_expired_accesses():
        return models.CustomerChatAccess.objects.filter(
            active=True,
            end_date__lt=timezone.now()
        ).all()

    @staticmethod
    def _revoke_access(access):
        for chat in access.chat_group.chats.all():
            bot.kick_chat_member(
                chat.chat_id, access.customer.chat_id
            )

    @staticmethod
    def _set_inactive(access):
        access.active = False
        access.save()

    @staticmethod
    def _notify_customer(access):
        return build_callback_inline_reply(
            customer=access.customer,
            app_name="accesser",
            reply_name="RevokeAccessNotificationReply",
            args=[access.id]
        )


