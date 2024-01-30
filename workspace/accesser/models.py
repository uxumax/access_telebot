from django.db import models
import main.models


# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()


class Transaction(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # Например: 'success', 'pending', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)


class AccessRecord(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    # chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    subscription = models.ForeignKey(
        "Subscription", on_delete=models.SET_NULL, null=True, blank=True
    )


class PaymentDetails(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    payment_method_type = models.CharField(
        max_length=50
    )  # Например: 'credit_card', 'paypal'
    last_four = models.CharField(max_length=4)
    expiration_date = models.DateField()
    token = models.CharField(
        max_length=100
    )  # Токен платежного метода, предоставляемый платежной системой
