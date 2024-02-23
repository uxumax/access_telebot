from django.contrib import admin
import main.models
import accesser.admin
import cashier.models

@admin.register(main.models.TelegramWebhook)
class TelegramWebhookAdmin(admin.ModelAdmin):
    list_display = ("pid", "url")


class BuildingInvoiceInline(admin.StackedInline):
    model = cashier.models.BuildingInvoice
    can_delete = False
    verbose_name_plural = 'building invoice'
    fk_name = 'customer'

    # Опционально, вы можете настроить поля, которые хотите отображать/скрыть
    # fields = ('subscription', 'duration', 'amount', 'network', 'currency', 'currency_type')
    # exclude = ('некоторое_поле',)


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
    inlines = [
        accesser.admin.CustomerChatAccessInline,
        BuildingInvoiceInline,
    ]


