#!/bin/bash

docker-compose stop
docker-compose pull app
docker-compose up -d