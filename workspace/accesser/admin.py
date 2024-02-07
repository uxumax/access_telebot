from django.contrib import admin
from . import forms
from . import models


class SubscriptionChatAccessInline(admin.TabularInline):
    model = models.SubscriptionChatAccess
    extra = 1  # Количество пустых форм для новых записей


class CustomerChatAccessInline(admin.TabularInline):
    model = models.CustomerChatAccess
    extra = 1  # Количество пустых форм для новых записей


@admin.register(models.ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_chats')
    search_fields = ('name',)
    filter_horizontal = ('chats',)

    def display_chats(self, obj):
        return ", ".join([chat.title for chat in obj.chats.all()])
    display_chats.short_description = 'Chats'


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    form = forms.ChatForm
    list_display = ('chat_id', 'title', 'chat_type', 'invite_link')
    list_filter = ('chat_type',)
    search_fields = ('title', 'chat_id')
    readonly_fields = ['title', 'chat_type', 'invite_link'] 

    def save_model(self, request, obj, form, change):
        data = form.chat_data
        obj.title = data.title
        obj.chat_type = data.type
        obj.invite_link = getattr(data, "invite_link",  None)
        super().save_model(request, obj, form, change)


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'duration')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    inlines = [SubscriptionChatAccessInline]


