#!/bin/bash

cd ../
docker-compose build
docker-compose run app python manage.py migrate
docker-compose run app python manage.py loaddata location
docker-compose up -d