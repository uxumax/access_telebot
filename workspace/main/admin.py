from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
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
                    "is_trial_used",
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
                    "last_notification_date",
                )
            },
        ),
    )
    inlines = [
        accesser.admin.CustomerChatAccessInline,
        accesser.admin.CustomerInviteLinkInline,
        BuildingInvoiceInline,
    ]

    list_display = (
        'chat_id',
        'username',
        'first_name',
        'last_name',
        'dialog_window_link',  # Add the custom button here
    )

    def dialog_window_link(self, obj):
        url = reverse('messenger:dialog_window_view', args=[obj.chat_id])
        return format_html('<a class="button" href="{}">Open Dialog</a>', url)

    dialog_window_link.short_description = 'Dialog Window'
    dialog_window_link.allow_tags = True

