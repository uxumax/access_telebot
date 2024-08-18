from access_telebot.logger import get_logger
import telebot

from main.workers import core
from accesser import models
from access_telebot.settings import (
    TELEBOT_KEY,
)

bot = telebot.TeleBot(TELEBOT_KEY)
log = get_logger(__name__)


class Worker(core.Worker):
    beat_interval = 60 * 5 
    stat = models.ChatUpdaterWorkerStat

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
        for chat in models.Chat.objects.all():
            tg_chat = self._get_tg_chat(chat)

            if tg_chat is None:
                log.warning(
                    f"Bot not subscribed to chat {chat.title}. "
                    "So it will be deleted"
                )
                chat.delete()
                # Note that new chats adding in main.views
                # with TelegramWebhookView._process_chat_member_update
                continue

            if chat.title != tg_chat.title:
                log.info(
                    "Changing Chat.title {chat.title} to {tg_chat.title}"
                )
                chat.title = tg_chat.title
                chat.save()

    @staticmethod
    def _get_tg_chat(chat: models.Chat):
        try: 
            tg_chat = bot.get_chat(chat.chat_id)
            return tg_chat
        except telebot.apihelper.ApiTelegramException as e:
            if "chat not found" in e.description:
                return None
            raise



