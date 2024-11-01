#!/bin/bash
set -e

PYTHON_ENV_PATH="/home/user/pyenv"

# Set permissions to env shared dir
chown -R user:user $PYTHON_ENV_PATH
su user

# Create and switch environmen
source $PYTHON_ENV_PATH/bin/activate

# Run workers
python manage.py run_all_workers
