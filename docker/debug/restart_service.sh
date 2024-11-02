if [ -z "$1" ]; then
  echo "Service name has not specified"
  exit 1
fi
docker compose down $1 && docker compose up $1
