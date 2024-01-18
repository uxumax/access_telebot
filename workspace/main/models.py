from django.db import models


class Customer(models.Model):
    chat_id = models.BigInterherField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    # Дополнительные поля, если необходимо
    # ...


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    subscription = models.ForeignKey(
        'Subscription', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    # Дополнительные поля, такие как описание подписки
    # ...


class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # Например: 'success', 'pending', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)
    # Дополнительные поля, связанные с платежной системой
    # ...


class Chat(models.Model):
    chat_id = models.BigInterherField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField()
    last_name = models.CharField()
    phone = models.CharField()
    # Дополнительные настройки доступа
    # ...


class AccessRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # Эта модель позволяет отслеживать, когда и как долго у пользователя есть доступ к чату


class PaymentDetails(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method_type = models.CharField(max_length=50) # Например: 'credit_card', 'paypal'
    last_four = models.CharField(max_length=4)
    expiration_date = models.DateField()
    token = models.CharField(max_length=100) # Токен платежного метода, предоставляемый платежной системой
    # Дополнительные данные платежного метода
    # ...
