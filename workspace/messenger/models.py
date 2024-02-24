from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class BotMessage(models.Model):
    text = models.TextField()
    # buttons = models.ManyToManyField('InlineButton', blank=True)

    def get_buttons(self):
        """
        Returns a queryset of InlineButton objects associated with this BotMessage.
        """
        content_type = ContentType.objects.get_for_model(self)
        return InlineButton.objects.filter(
            content_type=content_type, 
            object_id=self.id
        )


class InlineButton(models.Model):
    caption = models.CharField(max_length=255)
    reply = models.ForeignKey('CallbackInlineReply', on_delete=models.CASCADE)
    
    # Добавление полей для GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str((self.caption, self.reply))


class CallbackInlineReply(BotMessage):
    callback_data = models.SlugField(unique=True)
    message = models.OneToOneField(
        BotMessage, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="callback_inline_reply"
    )

    def __str__(self):
        return self.callback_data


class CommandReply(BotMessage):
    command = models.CharField(max_length=255)
    message = models.OneToOneField(
        BotMessage, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="command_reply"
    )

    def __str__(self):
        return self.command


class Notification(BotMessage):
    message = models.OneToOneField(
        BotMessage, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="notification"
    )

    alert_date = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)


class ShowedInlineButton(models.Model):
    caption = models.CharField(max_length=255, verbose_name='Caption')
    callback_data = models.CharField(max_length=255, unique=True, verbose_name='Callback Data')

    def __str__(self):
        return f"{self.caption} ({self.callback_data})"

    class Meta:
        verbose_name = 'Showed Inline Button'
        verbose_name_plural = 'Showed Inline Buttons'



