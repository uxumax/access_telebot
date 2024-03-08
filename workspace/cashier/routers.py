from . import replies
from messenger.routers import CallbackInlineRouterBase
import telebot
from access_telebot.settings import TELEBOT_KEY
from access_telebot.logger import get_logger

bot = telebot.TeleBot(TELEBOT_KEY, threaded=False)
log = get_logger(__name__)


class CallbackInlineRouter(CallbackInlineRouterBase):
    def route(self):
        _is = self.is_reply_name   

        if _is("ChooseAccessDurationReply"):
            return self.build_reply(replies.ChooseAccessDurationReply)

        if _is("ChoosePayMethodReply"):
            return self.build_reply(replies.ChoosePayMethodReply)
        
        if _is("CheckoutReply"):
            return self.build_reply(replies.CheckoutReply) 
             
        if _is("NotifyWhenTranzConfirmedReply"):
            return self.build_reply(replies.NotifyWhenTranzConfirmedReply) 
        
        if _is("CryptoTranzWaitReply"):
            return self.build_reply(replies.CryptoTranzWaitReply) 

        if _is("CryptoConfirmWaitReply"):
            return self.build_reply(replies.CryptoConfirmWaitReply) 
        
        if _is("CryptoPayDoneReply"):
            return self.build_reply(replies.CryptoPayDoneReply) 
        
        if _is("CryptoPayCancelReply"):
            return self.build_reply(replies.CryptoPayCancelReply) 
        
        if _is("CryptoPayResultReply"):
            return self.build_reply(replies.CryptoPayResultReply) 
        
        if _is("CryptoPayingReply"):
            return self.build_reply(replies.CryptoPayingReply) 

        return self.reply_not_found()
