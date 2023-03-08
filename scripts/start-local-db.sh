#!/bin/bash
set -e

# Start fresh container.
echo
echo "start-local-db: Starting postgres container"
echo "-------------------------------------------"
container_id=$(docker run \
    --name workout-api-postgres \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -d --rm \
    -p 6543:5432 \
    postgres:14.6)
sleep 1
echo "Container ID: $container_id"

# Run migrations.
echo
echo "start-local-db: Running migrations"
echo "----------------------------------"
alembic upgrade head

# Insert seed data
echo
echo "start-local-db: Running seed insertions"
echo "---------------------------------------"
here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
$here/run_seeds.sh

echo
