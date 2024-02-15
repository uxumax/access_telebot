

class CallbackInlineRouter:
    def __init__(
        self, 
        customer: main.models.Customer, 
        callback: telebot.types.CallbackQuery,
    ):
        self.customer = customer
        self.callback = callback

    def route(self):
        def _is(data: str):
            return self.callback.data == data        
        
        if _is("cashier_my_subs"):
            return self._build_reply(InlineReplyMySubs)

        if _is("cashier_all_subs"):
            return self._build_reply(InlineReplyAllSubs)

        bot.answer_callback_query(
            self.callback.id, 
            f"I don't know callback {self.callback.data}"
        )

    def _build_reply(
        self, 
        InlineReply: CallbackInlineReply
    ):
        bot.answer_callback_query(self.callback.id)
        return InlineReply(
            self.customer, self.callback
        ).build()