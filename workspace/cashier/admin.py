from django.contrib import admin
from . import models


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
