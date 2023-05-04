#!/usr/bin/env bash

docker run --rm --volumes-from wsmc_postgres_1 -v $(pwd):/backup ubuntu tar cvf /backup/db_backup.tar /var/lib/postgresql/data