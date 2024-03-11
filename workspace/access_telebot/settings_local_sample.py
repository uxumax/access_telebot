import logging
import base64

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'access_telebot',
        'USER': 'postgres',
        'PASSWORD': 'gotosu10',
        'HOST': 'localhost',
    },
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_URL_WAY = ""  # Set you secret admin page path"

TELEBOT_KEY = "Get key from @BotFather"
TELEBOT_WEBHOOK = {
    "type": "SERVEO",  # SERVEO is nice for run on local machine
    # "type": "HOST",  # HOST is nice for run on vps like
    # "host": "https://domain.com", # Can be IPv4 also
}

FIELD_ENCRYPTION_KEY = base64.urlsafe_b64encode(
    b"Use command generate_field_encryption_key for generate this key"
)

CSRF_TRUSTED_ORIGINS = [
    'https://domain.com'
]
ALLOWED_HOSTS_REGEX = [
    r"0\.0\.0\.0",
    r"127\.0\.0\.1",
    r'^[a-f0-9]{32}\.serveo\.net$',
]

LOG_LEVEL = logging.INFO
TRANSLATION = "Run command make_translation <translation_name> before"
PORT = 8001  # django/gunicorn port
TESTER_CHAT_ID = "Bot tester chat id"

from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

