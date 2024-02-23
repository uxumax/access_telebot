from django.contrib import admin
from django.utils import timezone
from . import models


@admin.register(models.CryptoInvoice)
class CryptoInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "subscription",
        "status",
        "network",
        "address",
        "amount",
        "currency",
        "paid_date",
    )
    list_filter = ("status", "network", "currency")
    search_fields = (
        "address",
        "customer__name",
        "subscription__id",
    )  # Adjust these fields based on your Customer and Subscription models
    date_hierarchy = "create_date"
    actions = ["mark_as_paid"]

    @admin.action(description="Mark selected invoices as paid")
    def mark_as_paid(self, request, queryset):
        queryset.update(status="PAID", paid_date=timezone.now())


@admin.register(models.CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ("invoice", "txid", "current_confirmations", "timestamp")
    list_filter = ("current_confirmations", "timestamp")
    search_fields = ("txid", "invoice__id")
    date_hierarchy = "timestamp"


@admin.register(models.TronAddress)
class TronAddressAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "status",
        "create_date",
    )  # Поля, которые будут отображаться в списке
    list_filter = ("status", "create_date")  # Фильтры по статусу и дате создания
    search_fields = ("address",)  # Поиск по адресу

    # При необходимости можно настроить и другие параметры административного интерфейса
