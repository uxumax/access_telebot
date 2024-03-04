from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import QuerySet

import main.models


class ChatTypeChoices(models.TextChoices):
    SUPERGROUP = 'supergroup', 'Supergroup'
    GIGAGROUP = 'gigagroup', 'Gigagroup'


class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    chats = models.ManyToManyField(
        'Chat', 
        related_name='chat_groups',
        blank=True
    )
    parent_group = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='child_groups',
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.name

    def get_all_child_chats(self) -> QuerySet:
        """
        Получает все чаты из текущей группы и ее дочерних групп рекурсивно.
        """
        chats = self.chats.all()
        for child_group in self.child_groups.all():
            chats = chats | child_group.get_all_child_chats()
        return chats.distinct()


class CustomerAccessRevokerWorkerStat(main.models.WorkerStatAbstract):
    """Worker stat model"""


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

    def __str__(self):
        return f"{self.title} ({self.chat_type})"

    def clean(self):
        super().clean()
        if self.invite_link:
            validator = URLValidator()
            try:
                validator(self.invite_link)
            except ValidationError as e:
                raise ValidationError({'invite_link': "Invalid URL."}) from e


class Subscription(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.name})"


class SubscriptionDurationPrice(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="durations"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(default=timedelta(days=30))    

    def __str__(self):
        return f"{self.subscription.name} | {self.duration} | {self.price}"


class SubscriptionChatAccess(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="access_to_chat_groups",
    )
    chat_group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        # related_name="subscription_accesses"
    )


class CustomerChatAccess(models.Model):
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"({self.id}:{self.customer.id}:{self.end_date})"


class InviteLink(models.Model):
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(main.models.Customer, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    access = models.ForeignKey(
        CustomerChatAccess, 
        on_delete=models.CASCADE,
        related_name="invite_links"
    )
    url = models.URLField()
    create_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField()
    member_limit = models.IntegerField(default=1)
    creates_join_request = models.BooleanField(default=False)

