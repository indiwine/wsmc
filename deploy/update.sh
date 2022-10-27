#!/bin/bash

cd ../
docker-compose stop
docker-compose pull app
docker-compose up -d