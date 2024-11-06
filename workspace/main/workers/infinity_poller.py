import os
from time import sleep
from main import models
from main.workers import core
from access_telebot.logger import get_logger
from main.views import bot

log = get_logger(__name__)


class Worker(core.Worker):
    # beat_interval = 60 * 5 
    stat = models.InfinityPollerWorkerStat

    def start(self):
        log.info("Start infinity polling")
        bot.delete_webhook()
        while True:
            try:
                bot.infinity_polling(
                    timeout=10,
                    long_polling_timeout=5,
                    skip_pending=os.getenv("SKIP_OLD_BOT_UPDATES_ON_NEW_START", "false") == 'true'
                )
            except Exception as e:
                wait_sec = 20
                log.warning(
                    f"Infinity polling crashed with {e}. "
                    f"Start another one after {wait_sec} "
                )
                sleep(wait_sec)
