from django.utils import timezone
from django.db.models import Q
from access_telebot.logger import get_logger
from datetime import timedelta
import telebot

from main.workers import core
from messenger.routers import build_callback_inline_reply
from messenger import models
from access_telebot.settings import (
    TELEBOT_KEY,
)

bot = telebot.TeleBot(TELEBOT_KEY)
log = get_logger(__name__)


class Worker(core.Worker):
    beat_interval = 60 * 5 
    stat = models.PeriodicNotifierWorkerStat

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
        notifications = self._get_all_notifications()
        if notifications.count() == 0:
            log.debug("No any notifications now")
            return

        for notification in notifications:
            log.debug(f"Sending notification {notification}")
            build_callback_inline_reply(
                notification.customer,
                app_name=notification.app_name,
                reply_name=notification.reply_name,
                args=notification.get_args()
            )
            notification.is_sent = True
            notification.save()

        # Set last notification date after all notifications sent
        for notification in notifications:
            notification.customer.last_notification_date = timezone.now()
            notification.customer.save()

    @staticmethod
    def _get_all_notifications():
        unannoy_threshold = timezone.now() - timedelta(days=1)
        return models.Notification.objects.filter(
            is_sent=False,
            # alert_date__lte=timezone.now(),
            # customer__last_notification_date__lte=unannoy_threshold,
        ).filter(
            Q(
                alert_date__isnull=True
            ) | Q(
                alert_date__lte=timezone.now()
            ),
            Q(
                customer__last_notification_date__isnull=True
            ) | Q(
                customer__last_notification_date__lte=unannoy_threshold
            )
        ).order_by("customer", "id").all()

