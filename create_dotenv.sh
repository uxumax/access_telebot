#!/bin/bash
#
if ! command -v openssl &> /dev/null
then
    echo "Please install `openssl` before run"
    exit 1
fi

generate_key() {
    length=$1
    new_key=$(openssl rand -base64 $length | tr '+/' '-_')
    echo "$new_key"
}

ask_for_telebot_api_key() {
  read -p "Please enter your Telegram Bot API key: " key 
  echo "$key"
}

ask_for_trongrid_api_key() {
  read -p "Please enter your TronGrid API key: " key 
  echo "$key"
}

env_vars="# AccessTelebot Docker services env variables
# Telegam bot and TronGrid API keys
TELEBOT_KEY=$(ask_for_telebot_api_key)
TRONGRID_KEY=$(ask_for_trongrid_api_key)

# Database field encryption passphrase for cryptocurrency wallet private keys
# Warning! If you lose this key, you may lose access to your USDT
# Note: If you migrate the database to another server, you must set this key on the new server to continue using your wallets
FIELD_ENCRYPTION_KEY=$(generate_key 32)

# Django admin superuser loging password and email
DJANGO_SUPERUSER_USERNAME=adminator
DJANGO_SUPERUSER_PASSWORD=$(generate_key 10)
DJANGO_SUPERUSER_EMAIL=some@email.com

# Secret URL path to the Django admin panel
# Default full URL to the admin panel: 127.0.0.1:8082/secret_way/admin
# By changing this parameter, you will modify the path to the admin panel
SECRET_URL_WAY=secret_way

# Nginx docker host port
NGINX_PORT=8082

# Domain name. Uncomment and set if using a domain name instead of an IP address.
# Only set the domain without 'http(s)://' or any other prefixes.
# DOMAIN_NAME=domain.com

# Postgres DB
POSTGRES_DB=access_telebot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(generate_key 10)
POSTGRES_HOST=postgres # db service name from docker-compose.yaml
POSTGRES_PORT=5445 # custom postgres port

# Use Telegam API webhook. 
# Set 'true' if the docker web service availabe by public IP or domain
USE_TELEGRAM_API_WEBHOOK=false

# Translation Name: Translation refers to changing bot text to your custom messages.
# Uncomment and set the name that you generated with the 'make_translations' command.
# TRANSLATION=translation_name

# Notify about expiration days before subscription ends
NOTIFIER_SUBSCRIPTION_EXPIRING_DAYS_BEFORE=2

# Default behavior is to wait some days after subscription expires
# Number of days to wait after subscription expires is set in 'WAIT_AFTER_SUBSCRIPTION_EXPIRED_DAYS'.
# Set to 'FORCE' if access needs to be revoked immediately after 'end_date'
DEFAULT_ACCESS_REVOKING_METHOD=GENTLE

# Revoke access after a certain number of days past 'access.end_date'
WAIT_AFTER_SUBSCRIPTION_EXPIRED_DAYS=6

# Skip bot update events from previous app start
# Set true if you have got Telegram API Error 
#   Code: 409 Description: 
#   Conflict: terminated by other getUpdates request
SKIP_OLD_BOT_UPDATES_ON_NEW_START=false

# Django debug mode
DJANGO_DEBUG=false

# Log level
LOG_LEVEL=INFO

# Customer chat id for tests
# TESTER_CHAT_ID=

# Python env path inside web service
PYTHON_ENV_PATH=/home/user/pyenv
"

echo -e "$env_vars" > .env
echo "The .env file gas been generated."
echo
echo "WARNING! Copy generated FIELD_ENCRYPTION_KEY from this file"
echo "Store it in a safe place. Without this key, you could lose the funds you receive from merchant sales."
