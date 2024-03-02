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

SECRET_URL_WAY = "mysecretway"

FIELD_ENCRYPTION_KEY = base64.urlsafe_b64encode(
    b"e0bc309cf0f362d87beb39451cd83321"
)

ALLOWED_HOSTS_REGEX = [
    r"0\.0\.0\.0",
    r"127\.0\.0\.1",
    r'^[a-f0-9]{32}\.serveo\.net$',
]

LOG_LEVEL = logging.DEBUG
TRANSLATION = None
