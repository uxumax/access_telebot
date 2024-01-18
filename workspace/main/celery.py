from celery import shared_task
from thrubot import logger


def log():
    return logger.get_module_logger("main.celery_tasks") 


@shared_task
def start_access_bot():
    import telebot

    API_KEY = 'ВАШ_ТЕЛЕГРАМ_БОТ_API_КЛЮЧ'
    bot = telebot.TeleBot(API_KEY)

    # Обработчик для команд, например, /start
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.reply_to(message, "Привет! Я ваш бот.")

    # Обработчик для обычных текстовых сообщений
    @bot.message_handler(func=lambda message: True)
    def handle_text_message(message):
        bot.reply_to(message, "Вы написали: " + message.text)

    # Запуск бота
    bot.polling(none_stop=True)

    # try:
    #     async_to_sync(listener.start)()
    #     log().info("ListenerBot started")
    # except Exception:
    #     log().exception("Issue with ListenerBot")
