from django.contrib import admin
from . import models
# from django.utils import timezone


class InlineButtonInline(admin.TabularInline):
    model = models.InlineButton
    extra = 1


@admin.register(models.CallbackInlineAnswer)
class CallbackInlineAnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'callback_label')
    inlines = [InlineButtonInline]


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('text', 'alert_date', 'is_sent')
    inlines = [InlineButtonInline]
