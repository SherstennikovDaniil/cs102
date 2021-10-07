#!/usr/bin/env bash

if [[ $(id -u) -ne -0 ]]; then
    echo "This script requires root privileges"
    exit 1
fi

if [[ -x "$(command -v docker)" ]]; then
    echo "Docker installed."
else
    echo "Docker not installed!"
    exit 2
fi

docker container inspect postgres-data > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Data volume container not found! Creating..."
    docker create -v /var/lib/postgresql/data --name postgres-data busybox
fi

docker run --name local-postgres -p 5432:5432 -e POSTGRES_PASSWORD=secret -d --volumes-from postgres-data --ip=127.0.0.1 --hostname localhost postgres:latest > /dev/null 2>&1

sleep 1

echo "Entering container. Please check if odscourse db exists."
docker exec -it local-postgres sh -c 'psql -U postgres'