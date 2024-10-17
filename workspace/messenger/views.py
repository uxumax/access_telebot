from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from telebot import TeleBot

from . import models

bot = TeleBot(settings.TELEBOT_KEY)


@staff_member_required
def dialog_window_view(request, chat_id):
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            bot.send_message(
                chat_id,
                text=text,
                parse_mode="HTML",
            )
            models.Message.objects.create(
                creator="2",
                chat_id=chat_id,
                text=text,
                date=timezone.now()
            )
            return redirect('dialog_window_view', chat_id=chat_id)

    messages = models.Message.objects.filter(chat_id=chat_id)
    return render(
        request,
        'messenger/dialog_window.html',
        context={
            "dialog_messages": messages,
        }
    )
