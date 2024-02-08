#!/bin/bash

#
# stop
#
CELERY_PIDS=$(cat celery.pid) &>/dev/null
kill -TERM $CELERY_PIDS &>/dev/null
celery -A access_telebot purge -f &>/dev/null
echo '' > celery.pid &>/dev/null

#
# start
#

# Запускаем Celery-воркер и записываем его идентификатор процесса в файл
# &>/dev/null
celery -A access_telebot worker --loglevel=error --logfile=logs/celery_worker.log --concurrency=2 &
echo $! >> celery.pid

sleep 3 

start_celery_task() {
    celery -A access_telebot call $1 #  &>/dev/null &
    echo "$1"
    echo $! >> celery.pid
}

# Проверка и создание файла PID, если необходимо
[[ -f celery.pid ]] || touch celery.pid

# Запуск задач Celery
start_celery_task main.celery.start_webhook_worker
start_celery_task accesser.celery.start_customer_access_revoke_worker

sleep 3