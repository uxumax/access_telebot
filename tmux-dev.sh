#!/bin/bash

# Название сессии tmux
SESSION_NAME="AccessTelebotDev"
VIM_WINDOW_HEIGHT=30
PORT=8002

# Проверка на существование сессии
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then

    # Создание новой сессии без окна
    tmux new-session -d -s $SESSION_NAME

    # Окно для сервера Django для runserver и command
    tmux new-window -t $SESSION_NAME -n Dev 

    # Разделение окна на две панели горизонтально
    tmux split-window -h -t $SESSION_NAME:1

    # Далее разделяем каждую из двух панелей вертикально
    tmux split-window -v -t $SESSION_NAME:1.0
    tmux split-window -v -t $SESSION_NAME:1.2

    # Dev Left-Up
    tmux send-keys -t $SESSION_NAME:1.0 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.0 "source ../env/bin/activate" C-m
    tmux send-keys -t $SESSION_NAME:1.0 "fuser -k $PORT/tcp" C-m
    # tmux send-keys -t $SESSION_NAME:1.0 "gunicorn --workers 3 --bind 0.0.0.0:8001 --access-logfile - --error-logfile -  access_telebot.wsgi:application" C-m
    tmux send-keys -t $SESSION_NAME:1.0 "python manage.py runserver 0.0.0.0:8001" C-m

    # Dev Left-Down
    tmux resize-pane -t $SESSION_NAME:1.1 -U $VIM_WINDOW_HEIGHT
    tmux send-keys -t $SESSION_NAME:1.1 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    # tmux send-keys -t $SESSION_NAME:1.1 "source ../env/bin/activate" C-m
    tmux send-keys -t $SESSION_NAME:1.1 "vim ." C-m
    
    # Dev Right-Up
    tmux send-keys -t $SESSION_NAME:1.2 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    tmux send-keys -t $SESSION_NAME:1.2 "source ../env/bin/activate" C-m

    # Dev Right-Down
    tmux resize-pane -t $SESSION_NAME:1.3 -U $VIM_WINDOW_HEIGHT
    tmux send-keys -t $SESSION_NAME:1.3 "cd /home/uxumax/dev/access_telebot/workspace" C-m
    # tmux send-keys -t $SESSION_NAME:1.3 "source ../env/bin/activate" C-m
    tmux send-keys -t $SESSION_NAME:1.3 "vim ." C-m
    
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
