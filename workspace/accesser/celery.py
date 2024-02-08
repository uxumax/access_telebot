from celery import shared_task
from access_telebot.logger import get_logger
from .workers import CustomerAccessRevokeWorker


log = get_logger(__name__)


@shared_task
def start_customer_access_revoke_worker():
    try:
        log.info("Customer access manager starting")
        CustomerAccessRevokeWorker().start_loop()
    except Exception as e:
        log.exception(e)
