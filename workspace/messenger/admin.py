from django.contrib import admin
from . import models
from django.utils import timezone
from django.contrib.contenttypes.admin import GenericTabularInline

from django.contrib import admin
from .models import InlineButton, CallbackInlineReply


class InlineButtonInline(GenericTabularInline):
    model = InlineButton
    extra = 1  # Установите количество дополнительных форм

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "callback_data":
            kwargs["queryset"] = CallbackInlineReply.objects.all()
            return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.CallbackInlineReply)
class CallbackInlineReplyAdmin(admin.ModelAdmin):
    list_display = ('callback_data', 'text')

    # field order
    fields = ('callback_data', 'text')

    inlines = [InlineButtonInline]


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('alert_date', 'is_sent')
    inlines = [InlineButtonInline]


@admin.register(models.CommandReply)
class CommandReplyAdmin(admin.ModelAdmin):
    # Определение отображаемых полей
    list_display = ('command', 'text')

    # Настройка фильтров
    list_filter = ('command',)

    # Настройка полей для поиска
    search_fields = ['command']

    # Порядок полей
    fields = ('command', 'text')

    inlines = [InlineButtonInline]

 
@admin.register(models.Translation) 
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'from_text', 'to_text')  
    search_fields = ('name', 'from_text', 'to_text')
    list_filter = ('name',)
    readonly_fields = ('name', 'from_text',)
    fields = ('name', 'from_text', 'to_text',)
