from django.contrib import admin
import main.models


@admin.register(main.models.TelegramWebhook)
class TelegramWebhookAdmin(admin.ModelAdmin):
    list_display = ("pid", "url")


@admin.register(main.models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Customer Info",
            {
                "fields": (
                    "chat_id",
                    "username",
                    "is_bot",
                    "first_name",
                    "last_name",
                    "language_code",
                    "phone",
                )
            },
        ),
        (
            "Customer Base Info",
            {
                "fields": (
                    "is_premium",
                    "added_to_attachment_menu",
                    "can_join_groups",
                    "can_read_all_group_messages",
                    "supports_inline_queries",
                    "last_callback_inline_date",
                )
            },
        ),
    )


# @admin.register(models.Subscription)
# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ("name", "price", "duration")
#     search_fields = ("name",)
#     list_filter = ("price",)
