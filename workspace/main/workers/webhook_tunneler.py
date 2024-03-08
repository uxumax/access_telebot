from access_telebot.logger import get_logger
from access_telebot.serveo_tunnel_maker import ServeoTunnelMaker
import typing

from django.conf import settings
from main import models
from main.workers import core
import requests
import telebot
from time import sleep
from access_telebot.settings import (
    TELEBOT_KEY,
    SECRET_URL_WAY
)

log = get_logger(__name__)
bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)


class TelegramWebhooker:
    log = get_logger(__name__)
    
    @staticmethod
    def get_current_webhook_url() -> typing.Union['str', None]:
        webhook = models.TelegramWebhook.load()
        return webhook.url

    @staticmethod
    def _save_new_webhook(new_pid: int, new_url: str):
        webhook = models.TelegramWebhook.load()
        webhook.url = new_url
        webhook.pid = new_pid
        webhook.save()

    @staticmethod
    def is_webhook_working(webhook_url: str) -> bool:
        """
        Checks if the webhook is working by sending a GET request to the webhook URL with a 5-second timeout.

        Args:
            webhook_url (str): The URL of the webhook to be checked.

        Returns:
            bool: True if the webhook is working (status code 200 or 201), otherwise False.
        """
        try:
            # Added timeout=5 to specify a 5-second timeout for the request
            response = requests.get(webhook_url, timeout=5)
            if response.status_code in [200, 201]:
                log.info(f"Webhook is still working {webhook_url}")
                return True
            else:
                log.warning(f"Webhook check failed with status code: {response.status_code}")
                return False
        except Exception as e:
            log.warning(f"Error checking webhook: {e}")
            return False

    @classmethod
    def make_webhook(cls):
        maker = ServeoTunnelMaker(settings.PORT)
        pid, serveo_host = maker.make()
        webhook_url = f"{serveo_host}/{SECRET_URL_WAY}/main/telegram_webhook/"
        cls._save_new_webhook(pid, webhook_url)
        return pid, webhook_url

    @classmethod
    def get_new_webhook_url(cls):
        pid, webhook_url = cls.make_webhook()
        return webhook_url

    @classmethod
    def get_webhook_url(cls):
        url = cls.get_current_webhook_url()

        cls.log.info(
            "Checking webhook..."
        )

        if url is not None:
            if cls.is_webhook_working(url):
                return url
        
        cls.log.info(
            f"Current webhook url: {url} is not working"
            " Create new one..."
        )
        
        url = cls.get_new_webhook_url()
        if not cls.is_webhook_working(url):
            raise Exception(
                "Has been made new webhook but new tunnel not working too"
            )

        cls.log.info(
            f"New webhook has been made and working: {url}"
        )

        return url


class WebhookUrlIsNotWorkingException(Exception):
    pass


class Worker(core.Worker):
    stat = models.WebhookTunnelerWorkerStat
    beat_interval = 10

    log = get_logger(__name__)
    webhooker = TelegramWebhooker

    def start(self):
        webhook_url = self.webhooker.get_webhook_url()
        bot.delete_webhook()
        bot.set_webhook(url=webhook_url)        

        while not self.stop_event.is_set():
            self._beat(webhook_url)
            self.wait()

    def _beat(self, webhook_url: str):
        try:
            self._check_webhook_url(webhook_url)
        except WebhookUrlIsNotWorkingException:
            return self.start()

    
    def _check_webhook_url(self, webhook_url):
        if self.webhooker.is_webhook_working(webhook_url):
            return
        else:
            raise WebhookUrlIsNotWorkingException(
                "Webhook is not working"
            )

