from celery import shared_task
from access_telebot.logger import get_logger
from .workers import (
    customer_access_revoker,
)


log = get_logger(__name__)


@shared_task
def start_customer_access_revoker():
    try:
        log.info("Customer access revoker starting")
        customer_access_revoker.start() 
    except Exception as e:
        log.exception(e)
