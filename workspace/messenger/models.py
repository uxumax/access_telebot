from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

import main.models


class PeriodicNotifierWorkerStat(main.models.WorkerStatAbstract):
    """Worker stat model"""


class CustomReplyBase(models.Model):
    text = models.TextField()

    def get_buttons(self):
        """
        Returns a queryset of InlineButton objects associated with this CustomReplyBase.
        """
        content_type = ContentType.objects.get_for_model(self)
        return CustomReplyInlineButton.objects.filter(
            content_type=content_type, 
            object_id=self.id
        )


class CustomReplyInlineButton(models.Model):
    caption = models.CharField(max_length=255)
    reply = models.ForeignKey('CallbackInlineReply', on_delete=models.CASCADE)
    
    # Добавление полей для GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str((self.caption, self.reply))


class CallbackInlineReply(CustomReplyBase):
    callback_data = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Example: custom&2&custom_replyname",
    )
    message = models.OneToOneField(
        CustomReplyBase, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="callback_inline_reply"
    )

    def __str__(self):
        return self.callback_data


class CommandReply(CustomReplyBase):
    command = models.CharField(
        max_length=255,
        unique=True,
        help_text="Set without `/`. Example: `get_company_info`",
    )
    message = models.OneToOneField(
        CustomReplyBase, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="command_reply"
    )

    def __str__(self):
        return self.command


class Notification(models.Model):
    customer = models.ForeignKey(
        main.models.Customer,
        on_delete=models.CASCADE, 
        related_name="notifications"
    )
    app_name = models.CharField(
        max_length=255,
        help_text="Django application name of CallbackInlineReply",
    )
    reply_name = models.CharField(
        max_length=255,
        help_text="CallbackInlineReply name",
    )
    args = models.CharField(
        max_length=2024,
        help_text="Separated by '&'; Example: 'arg1&arg2&arg3'"
    )
    # message = models.OneToOneField(
    #     CustomReplyBase, 
    #     on_delete=models.CASCADE, 
    #     parent_link=True, 
    #     related_name="notification"
    # )

    alert_date = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)

    def get_args(self) -> list:
        return self.args.split("&")


class ShowedInlineButton(models.Model):
    caption = models.CharField(max_length=255, verbose_name='Caption')
    callback_data = models.CharField(max_length=255, unique=True, verbose_name='Callback Data')

    def __str__(self):
        return f"{self.caption} ({self.callback_data})"

    class Meta:
        verbose_name = 'Showed Inline Button'
        verbose_name_plural = 'Showed Inline Buttons'


class Translation(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    from_text = models.TextField(
        unique=True,
        max_length=4096,
    )  # 4096 is maximum length of telegram msg
    to_text = models.TextField(
        null=True,
        max_length=4096,
    )

    def __str__(self):
        return f"{self.id}:{self.name}:{self.from_text[:10]}"
