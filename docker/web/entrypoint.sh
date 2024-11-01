#!/bin/bash
set -e

PYTHON_ENV_PATH="/home/user/pyenv"

# Set permissions to env shared dir
echo "Set user owner of python env dir"
chown -R user:user $PYTHON_ENV_PATH
echo "Swith to user"
su user

# Create and switch environmen
echo "Make python env"
if [ -z "$(ls -A $PYTHON_ENV_PATH)" ]; then
    echo "Python env is empty. So have to create it" 
    python -m venv $PYTHON_ENV_PATH
else
    echo "Python env already exists"
fi
echo "Activate python env"
source $PYTHON_ENV_PATH/bin/activate

echo "Install pip dependencies"
pip install --no-cache-dir -r ./requirements.txt 

echo "Migrate db"
python manage.py migrate

echo "Make staticfiles"
python manage.py collectstatic --no-input

echo "Create django superuser"
output=$( { python manage.py createsuperuser --no-input; } 2>&1 ) || true
if echo "$output" | grep -q "That username is already taken"; then
    echo "Django superuser already exists"
elif echo "$output" | grep -q "Superuser created successfully"; then
    echo "Superuser created"
else
    echo "$output"
    exit 1
fi

echo "Run web server"
gunicorn access_telebot.wsgi:application --bind 0.0.0.0:8000
