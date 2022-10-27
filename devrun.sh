#!/usr/bin/env bash

#set -e
#
#. .env

docker-compose -f docker-compose.yaml -f docker-compose-dev.yaml $@
