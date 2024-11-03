#!/bin/bash

get_env_file_path() {
    docker_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    env_file_path="$docker_dir/../.env"
    echo $env_file_path
}
source $(get_env_file_path)

CMD="$PYTHON_ENV_PATH/bin/python3 manage.py $@"
docker compose exec web $CMD
