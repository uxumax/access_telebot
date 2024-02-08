from celery import shared_task
from access_telebot.logger import get_logger
from .workers import WebHookTunnelWorker


log = get_logger(__name__)


@shared_task
def start_webhook_worker():
    try:
        log.info("Webhook worker starting")
        WebHookTunnelWorker().start_loop()
    except Exception as e:
        log.exception(e)
