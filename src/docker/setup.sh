#!/bin/sh
set -e
set -o pipefail

if ! command -v docker >/dev/null 2>&1; then
  printf "ERROR: Docker is not installed or not available in PATH.\n"
  printf "Please install Docker and retry.\n"
  exit 1
fi

cd "$(dirname "$0")"
mkdir -p logs

docker-compose build

docker-compose up --detach
printf "Waiting for test containers to finish\n"
docker-compose wait auth_test authorization_test content_test

docker-compose logs --no-color --tail=100

docker-compose down

printf "\nPipeline completed. Log is available at %s/logs/api_test.log\n" "$(pwd)"
