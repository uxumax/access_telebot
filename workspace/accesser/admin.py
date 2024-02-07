from django.contrib import admin
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
    list_display = ('chat_id', 'title', 'chat_type', 'invite_link')
    list_filter = ('chat_type',)
    search_fields = ('title', 'chat_id')


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'duration')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    inlines = [SubscriptionChatAccessInline]


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'subscription', 'transaction_id', 'amount', 'status', 'timestamp')
    list_filter = ('status', 'customer')
    search_fields = ('customer__name', 'transaction_id', 'status')


@admin.register(models.PaymentDetails)
class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'payment_method_type', 'last_four', 'expiration_date', 'token')
    list_filter = ('payment_method_type',)
    search_fields = ('customer__name', 'payment_method_type')
