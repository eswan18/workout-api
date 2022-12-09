#!/bin/bash
set -e

# Start fresh container.
docker run \
    --name workout-api-postgres \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -d --rm \
    -p 6543:5432 \
    postgres:14.6
sleep 1
# Run migrations.
alembic upgrade head
# Insert seed data
here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
$here/run_seeds.sh
