from django.db import models
from django.utils import timezone


class BotMessage(models.Model):
    text = models.TextField()


class InlineButton(models.Model):
    message = models.ForeignKey(
        BotMessage, on_delete=models.CASCADE, related_name="buttons"
    )
    callback_label = models.CharField(max_length=255)


class CallbackInlineAnswer(BotMessage):
    message = models.OneToOneField(
        BotMessage, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="callback"
    )
    callback_label = models.SlugField(unique=True)


class Notification(BotMessage):
    message = models.OneToOneField(
        BotMessage, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="notification"
    )
    alert_date = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)
