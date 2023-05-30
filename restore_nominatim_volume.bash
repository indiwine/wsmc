#!/usr/bin/env bash

docker run --rm --volumes-from wsmc-nominatim-1 -v $(pwd):/backup ubuntu bash -c "cd /var && tar xvf /backup/nominatim_backup.tar --strip 1"