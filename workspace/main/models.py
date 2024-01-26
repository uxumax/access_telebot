from django.db import models


class SingletonModel(models.Model):
    """
    Django model for a singleton instance.
    Only one instance of this model can exist in the database.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save method overridden to ensure only one instance exists.
        """
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load or create the singleton instance.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ProjectSettings(SingletonModel):
    """
    Model to store project settings.
    Inherits from SingletonModel to ensure only one instance.
    """
    telegram_webhook_url = models.URLField(null=True, default=None)
    telegram_webhook_pid = models.IntegerField(null=True, default=None)
    
    def __str__(self):
        return "Project Settings"


class Customer(models.Model):
    chat_id = models.BigIntegerField(unique=True)  # Existing field for chat ID
    username = models.CharField(max_length=100, blank=True, null=True)  # Existing field for username
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_premium = models.BooleanField(default=False, null=True)
    added_to_attachment_menu = models.BooleanField(default=False, null=True)
    can_join_groups = models.BooleanField(default=False, null=True)
    can_read_all_group_messages = models.BooleanField(default=False, null=True)
    supports_inline_queries = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.username or self.first_name


class Chat(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField()
    last_name = models.CharField()
    phone = models.CharField()


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()


class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # Например: 'success', 'pending', 'failed'
    timestamp = models.DateTimeField(auto_now_add=True)


class AccessRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    subscription = models.ForeignKey(
        'Subscription', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )


class PaymentDetails(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method_type = models.CharField(max_length=50)  # Например: 'credit_card', 'paypal'
    last_four = models.CharField(max_length=4)
    expiration_date = models.DateField()
    token = models.CharField(max_length=100)   # Токен платежного метода, предоставляемый платежной системой