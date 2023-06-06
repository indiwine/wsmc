#!/usr/bin/env bash

set -e

. .env

docker stack deploy -c docker-compose.yaml wsmc