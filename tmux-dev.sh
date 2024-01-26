#!/bin/bash

# Название сессии tmux
SESSION_NAME="AccessTelebotDev"


# Проверка на существование сессии
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  # Создание новой сессии без окна
  tmux new-session -d -s $SESSION_NAME

  # Окно для сервера Django для runserver и command
  tmux new-window -t $SESSION_NAME -n Django
  tmux split-window -v -t Django -p 50
  # Настройка верхней панели (runserver)
  tmux send-keys -t Django.0 "cd /home/uxumax/dev/access_telebot/workspace" C-m
  tmux send-keys -t Django.0 "source ../env/bin/activate" C-m
  tmux send-keys -t Django.0 "python3.11 manage.py runserver 8001" C-m
  # Настройка нижней панели (command)
  tmux send-keys -t Django.1 "cd /home/uxumax/dev/access_telebot/workspace" C-m
  tmux send-keys -t Django.1 "source ../env/bin/activate" C-m
fi

# Подключение к созданной сессии
tmux attach -t $SESSION_NAME
