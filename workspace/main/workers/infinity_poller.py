from main import models
from main.workers import core
from access_telebot.logger import get_logger
from main.views import bot


from access_telebot.settings import (
    TELEBOT_KEY,
)

# bot = telebot.TeleBot(TELEBOT_KEY)
log = get_logger(__name__)


class Worker(core.Worker):
    # beat_interval = 60 * 5 
    stat = models.InfinityPollerWorkerStat

    def start(self):
        log.info("Start infinity polling")
        bot.delete_webhook()
        bot.infinity_polling(  # Should have infinity loop inside
            timeout=10,
            long_polling_timeout=5
        )
