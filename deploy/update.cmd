@echo off

echo "Fetching changes from github"
git pull

echo "Stopping"
docker-compose stop

echo "Pulling update"
docker-compose pull app

echo "Applying migrations"
docker-compose run --rm app python manage.py migrate

echo "Setting back"
docker-compose up -d

echo "Cleaning"
docker image prune

echo "All done"
pause
