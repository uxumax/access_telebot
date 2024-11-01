#!/bin/bash
set -e

change_shared_dirs_owner() {
  echo "Change shared dir owner"
  sudo chown -R $USER:$USER docker/postgres/data || true
  sudo chown -R $USER:$USER docker/pyenv || true
  sudo chown -R $USER:$USER workspace 
}

remove_postgres_data_and_migrations() {
  echo "Remove postgres data"
  rm -rf docker/postgres/data || true

  echo "Remove migrations"
  rm -rf workspace/messenger/migrations || true
  rm -rf workspace/accesser/migrations || true
  rm -rf workspace/cashier/migrations || true
  rm -rf workspace/main/migrations || true
}

remove_python_env() {
  echo "Remove python env" 
  rm -rf docker/pyenv || true
}


docker compose down
change_shared_dirs_owner
if [ "$1" == "--total" ]; then
  remove_postgres_data_and_migrations
  remove_python_env
elif [ "$1" == "--postgres" ]; then
  remove_postgres_data_and_migrations
fi
docker compose build
docker compose up
