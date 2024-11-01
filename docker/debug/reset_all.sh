#!/bin/bash
set -e

if [ "$1" == "--total" ]; then
  # Total case
  docker compose down

  sudo chown -R $USER:$USER docker/postgres/data || true
  # sudo chown -R $USER:$USER docker/pyenv || true
  sudo rm -rf docker/postgres/data || true
  # sudo rm -rf docker/pyenv || true

  docker compose build --no-cache
  docker compose build
  docker compose up
else
  # Default case
  docker compose down
  docker compose build
  docker compose up
fi
