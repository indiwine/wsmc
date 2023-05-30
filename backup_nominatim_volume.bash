#!/usr/bin/env bash

docker run --rm --volumes-from wsmc-nominatim-1 -v $(pwd):/backup ubuntu tar cvf /backup/nominatim_backup.tar /var/lib/postgresql/14/main