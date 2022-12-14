#!/bin/bash

docker-compose build
echo "Wating for a while for PG to initialize"
sleep 30
docker-compose run app python manage.py migrate
docker-compose run app python manage.py loaddata location
echo "Create a password for admin user:"
docker-compose run app python manage.py createsuperuser --username admin --email admin@example.com
docker-compose up -d