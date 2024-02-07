from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import (
    Chat,
)
import telebot


bot = telebot.TeleBot(settings.TELEBOT_KEY)


class ChatForm(forms.ModelForm):
    chat_data: telebot.types.Chat
    # The chat_data attribute is used to temporarily store the data of a Telegram chat
    # retrieved via the Telegram Bot API (using telebot.types.Chat) during form validation.
    # This attribute allows for storing chat data fetched from an external API call
    # within the form's lifecycle, enabling the use of this data in the form's save process
    # without needing to make another API call. It is particularly useful for scenarios
    # where the chat data fetched during form validation needs to be used or validated
    # further before the form is saved, ensuring that all necessary chat information
    # is readily available and up-to-date at the point of saving.

    class Meta:
        model = Chat
        fields = ['chat_id']  # Указываем, что форма должна содержать только chat_id

    def clean(self):
        cleaned_data = super().clean()
        
        chat_id = cleaned_data.get("chat_id")
        self._set_chat_data(chat_id)

        return cleaned_data

    def _set_chat_data(self, chat_id):
        try:
            chat_data = bot.get_chat(chat_id)
            self.chat_data = chat_data
        except telebot.apihelper.ApiTelegramException as e:
            raise ValidationError({
                "chat_id": f"Cannot find chat with ID: {chat_id}. Error: {str(e)}"
            }) 