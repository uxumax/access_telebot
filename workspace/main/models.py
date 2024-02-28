from django.db import models
from django.utils import timezone


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


class TelegramWebhook(SingletonModel):
    url = models.URLField(null=True, default=None)
    pid = models.IntegerField(null=True, default=None)

    def __str__(self):
        return f"TelegramWebhook({self.pid}, {self.url})"


class CustomerBase(models.Model):  # System base class
    # Telebot data
    is_premium = models.BooleanField(
        default=False, null=True
    )  # Является ли пользователь премиум-пользователем
    added_to_attachment_menu = models.BooleanField(
        default=False, null=True
    )  # Добавлен ли пользователь в меню вложений
    can_join_groups = models.BooleanField(
        default=False, null=True
    )  # Может ли пользователь присоединяться к группам
    can_read_all_group_messages = models.BooleanField(
        default=False, null=True
    )  # Может ли пользователь читать все сообщения группы
    supports_inline_queries = models.BooleanField(
        default=False, null=True
    )  # Поддерживает ли пользователь inline-запросы    

    # Local data
    last_callback_inline_date = models.DateTimeField(
        default=timezone.make_aware(timezone.datetime(1970, 1, 1))
    )  # Время последнего callback-вызова


class Customer(CustomerBase):
    base = models.OneToOneField(
        CustomerBase, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        related_name="notification"
    )
    # Основные данные, связанные с Chat телебота
    chat_id = models.BigIntegerField(unique=True)  # ID чата в Telegram
    username = models.CharField(
        max_length=100, blank=True, null=True
    )  # Имя пользователя Telegram
    is_bot = models.BooleanField(default=False)  # Является ли пользователь ботом
    first_name = models.CharField(
        max_length=255, blank=True, null=True
    )  # Имя пользователя
    last_name = models.CharField(
        max_length=255, blank=True, null=True
    )  # Фамилия пользователя
    language_code = models.CharField(
        max_length=10, blank=True, null=True
    )  # Код языка пользователя
    phone = models.CharField(
        max_length=30, blank=True, null=True
    )

    def __str__(self):
        return self.username or self.first_name


class WorkerStatAbstract(SingletonModel):
    last_beat_date = models.DateTimeField(
        default=timezone.make_aware(timezone.datetime(1970, 1, 1))
    )

    class Meta:
        abstract = True


class WebhookTunnelerWorkerStat(WorkerStatAbstract):
    """Worker stat model"""
