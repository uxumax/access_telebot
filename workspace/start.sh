#!/bin/bash

#
# stop
#

UWSGI_PIDS=$(cat uwsgi.pid) &>/dev/null
kill -TERM $UWSGI_PIDS &>/dev/null

CELERY_PIDS=$(cat celery.pid) &>/dev/null
kill -TERM $CELERY_PIDS &>/dev/null
celery -A thrubot purge -f &>/dev/null
echo '' > celery.pid &>/dev/null

#
# start
#

# Запускаем Celery-воркер и записываем его идентификатор процесса в файл
# &>/dev/null
celery -A thrubot worker --loglevel=error --logfile=logs/celery_worker.log --concurrency=1 &
echo $! >> celery.pid

sleep 3 

start_celery_task() {
    celery -A thrubot call $1 &>/dev/null &
    echo "$1"
    echo $! >> celery.pid
}

# Проверка и создание файла PID, если необходимо
[[ -f celery.pid ]] || touch celery.pid

# Запуск задач Celery
start_celery_task main.celery.start_access_bot

# # Запускаем Celery-шедулер (beat) и записываем его идентификатор процесса в файл
# celery -A thrubot beat --loglevel=error --logfile=logs/celery_beat.log &>/dev/null &
# echo $! >> celery.pid

sleep 3