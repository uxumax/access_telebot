from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

import main.models


class ChatTypeChoices(models.TextChoices):
    SUPERGROUP = 'supergroup', 'Supergroup'
    GIGAGROUP = 'gigagroup', 'Gigagroup'


class Chat(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    chat_type = models.CharField(
        max_length=25,
        choices=ChatTypeChoices.choices,
        default=ChatTypeChoices.SUPERGROUP
    )
    invite_link = models.URLField(
        max_length=1024, 
        blank=True, 
        null=True
    )

    def clean(self):
        super().clean()
        if self.invite_link:
            validator = URLValidator()
            try:
                validator(self.invite_link)
            except ValidationError as e:
                raise ValidationError({'invite_link': "Invalid URL."}) from e

    def __str__(self):
        return f"{self.title} ({self.get_chat_type_display()})"


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()


class SubscriptionChatAccess(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="access_to_chats"
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="subscription_accesses"
    )


class CustomerChatAccess(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )


def create_access_records(customer_id: int, subscription_id: int):
    from django.utils import timezone
    customer = main.models.Customer.objects.get(id=customer_id)
    subscription = Subscription.objects.get(id=subscription_id)
    access_types = subscription.access_types.all()
    for access_type in access_types:
        CustomerChatAccess.objects.create(
            customer=customer,
            start_date=timezone.now(),
            end_date=timezone.now() + subscription.duration,
            subscription=subscription
        )


class Transaction(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # Например: 'success', 'pending', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)


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



