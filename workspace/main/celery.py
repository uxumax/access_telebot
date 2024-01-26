from celery import shared_task
from access_telebot.logger import get_logger
import main.workers


log = get_logger(__name__)


@shared_task
def start_webhook_worker():
    try:
        main.workers.WebHookTunnelWorker().start_loop()
    except Exception as e:
        log.exception(e)
