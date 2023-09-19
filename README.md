# WSMC - Wartime Social Media Crawler

A Django based scraping tool.

## How to start
### For users
1. Install [docker](https://docs.docker.com/get-docker/) (and possibly docker compose) 
2. Rename [.env.example](.env.example) into `.env` and put appropriate values there 
3. Run install script from a deploy folder (you will be asked for an admin user password at some point)

Start and stop can be done from a `docker desktop` app or by issuing `docker-compose stop`
and `docker-compose up -d` commands in a project root directory.
### For developers
1. See steps 1 - 3 above
2. Use `./devrun.sh` instead of `docker-compose` command

### Locations
- Default address of the interface is [localhost:8000](http://localhost:8000) 
- Default address of the noVNC at Selenium grid machine is [localhost:7900](http://localhost:7900)


## TODO:
1. Add unit tests (at least for most critical places)
2. Find a way to switch of debug mode for a regular user - right now we are losing ability to serve static files
3. I18n, maybe...
4. Switch to docker compose V2 once it will be stable
