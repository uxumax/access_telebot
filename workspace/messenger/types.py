import main.models
import telebot


class CallbackInlineRouterBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback


 class CallbackInlineReplyBuilderBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery
    ):
        self.customer = customer
        self.callback = callback


 class CommandReplyBuilderBase:
    def __init__(
        self, 
        customer: main.models.Customer, 
        message: telebot.types.Message,
    ):
        self.customer = customer
        self.message = message