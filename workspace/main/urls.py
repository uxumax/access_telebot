from django.urls import path

from . import views

urlpatterns = [
    path(
        'telegram_webhook/',
        views.TelegramWebhookView.as_view(), 
        name='telegram_webhook'
    ),
]