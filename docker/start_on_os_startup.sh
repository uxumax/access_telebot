#/bin/bash

sudo systemctl enable docker
docker compose down 
docker compose stop
docker compose rm -f
docker compose create
docker compose start
