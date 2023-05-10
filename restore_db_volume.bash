#!/usr/bin/env bash

docker run --rm --volumes-from wsmc-postgres-1 -v $(pwd):/backup ubuntu bash -c "cd /var && tar xvf /backup/db_backup.tar --strip 1"