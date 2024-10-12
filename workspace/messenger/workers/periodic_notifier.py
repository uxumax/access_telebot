from django.utils import timezone
from access_telebot.logger import get_logger
import telebot

from main.workers import core
from messenger.routers import build_callback_inline_reply
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
            try:
                self._beat()
                self.wait()
            except Exception as e:
                log.exception(e)
                break

        log.warning(f"Worker:{__name__} has been stopped")
        return

    def _beat(self):
        customers = self._get_all_customers()
        if customers.count() == 0:
            return

        pass

    @staticmethod
    def _get_all_notifications():
        return messenger.models.MessageReply.objects.filter(

        ).all()

    # @staticmethod
    # def _get_all_customers():
    #     return main.models.Customer.objects.filter(
    #     ).all()

