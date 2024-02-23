#!/bin/bash

# Название сессии tmux
SESSION_NAME="AccessTelebotDev"


# Проверка на существование сессии
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then

    # Создание новой сессии без окна
    tmux new-session -d -s $SESSION_NAME

    # Окно для сервера Django для runserver и command
    tmux new-window -t $SESSION_NAME -n Debug 

    # Разделение окна на две панели горизонтально
    tmux split-window -h -t $SESSION_NAME:1

    # Далее разделяем каждую из двух панелей вертикально
    tmux split-window -v -t $SESSION_NAME:1.0
    tmux split-window -v -t $SESSION_NAME:1.2

    # Настройка панели 1 (левый верхний квадрант)
    tmux send-keys -t $SESSION_NAME:1.0 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.0 "source ../env/bin/activate" C-m
    tmux send-keys -t $SESSION_NAME:1.0 "python3.11 manage.py runserver 8001" C-m

    # Повторяем настройку для других панелей
    tmux send-keys -t $SESSION_NAME:1.1 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.1 "source ../env/bin/activate" C-m

    tmux send-keys -t $SESSION_NAME:1.2 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.2 "source ../env/bin/activate" C-m

    tmux send-keys -t $SESSION_NAME:1.3 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.3 "source ../env/bin/activate" C-m
    
    # Окно для работы с Git
    tmux new-window -t $SESSION_NAME -n Git
    tmux send-keys -t Git "cd /home/uxumax/dev/access_telebot/" C-m

    # Окно для работы с PostgreSQL
    tmux new-window -t $SESSION_NAME -n PostgreSQL
    tmux send-keys -t PostgreSQL "sudo -u postgres psql" C-m
    tmux send-keys -t PostgreSQL "gotosu10" C-m
fi

# Подключение к созданной сессии
tmux attach -t $SESSION_NAME
