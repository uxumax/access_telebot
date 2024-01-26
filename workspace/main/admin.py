from django.contrib import admin
from main import models


@admin.register(models.ProjectSettings)
class ProjectSettingsAdmin(admin.ModelAdmin):
    list_display = ("telegram_webhook_url", "telegram_webhook_pid")


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "chat_id",
        "username",
        "is_bot",
        "first_name",
        "last_name",
        "language_code",
        "is_premium",
        "added_to_attachment_menu",
        "can_join_groups",
        "can_read_all_group_messages",
        "supports_inline_queries",
    )
    search_fields = ("username", "first_name", "last_name")
    list_filter = (
        "is_bot",
        "is_premium",
        "can_join_groups",
        "can_read_all_group_messages",
        "supports_inline_queries",
    )


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "username", "first_name", "last_name", "phone")
    search_fields = ("username", "first_name", "last_name", "phone")


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration")
    search_fields = ("name",)
    list_filter = ("price",)
