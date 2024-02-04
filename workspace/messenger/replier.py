import main.models
import telebot.types
from . import replier_dynamic
# from . import replier_static


def handle_callback_inline(
    customer: main.models.Customer, 
    callback: telebot.types.CallbackQuery
):
    replier_dynamic.CallbackInlineReply(
        customer, callback
    ).build()


def handle_command(
    customer: main.models.Customer, 
    message: telebot.types.CallbackQuery
):
    replier_dynamic.CommandReply(
        customer, message
    ).build()