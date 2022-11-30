echo "Fetching changes from github"
git pull

echo "Stopping our setup"
docker-compose stop
echo "Pulling update"
docker-compose pull app
echo "Setting back"
docker-compose up -d
