#!/bin/bash

#
# stop
#

UWSGI_PIDS=$(cat uwsgi.pid) &>/dev/null
kill -TERM $UWSGI_PIDS &>/dev/null

CELERY_PIDS=$(cat celery.pid) &>/dev/null
kill -TERM $CELERY_PIDS &>/dev/null
celery -A access_telebot purge -f &>/dev/null
echo '' > celery.pid &>/dev/null