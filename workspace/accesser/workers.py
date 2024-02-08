from django.utils import timezone
from access_telebot.logger import get_logger
import telebot
from time import sleep
from . import models
from access_telebot.settings import (
    TELEBOT_KEY,
)

bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


class CustomerAccessRevokeWorker:
    log = get_logger(__name__, "CustomerAccessRevokeWorker")

    def start_loop(self):
        while True:
            self._beat()
            sleep(60 * 60 * 1)  # 1 hour

    def _beat(self):
        for access in self._get_all_expired_accesses():
            return self._revoke_access(access)

    @staticmethod
    def _get_all_expired_accesses():
        return models.CustomerChatAccess.objects.filter(
            end_date__lt=timezone.now()  # Истекшие доступы, где 'end_date' меньше текущего времени
        ).all()

    @classmethod
    def _revoke_access(cls, access):
        for chat in access.chat_group.chats.all():
            bot.kick_chat_member(
                chat.chat_id, access.customer.chat_id
            )
        cls.log.info(
            f"Access {access} has been revoked"
        )
