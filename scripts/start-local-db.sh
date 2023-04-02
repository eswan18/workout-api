#!/bin/bash
set -e

container_name="workout-api-postgres"

# Check if the container is already running
matching_containers=$(docker ps -f "name=${container_name}" --quiet | wc -l)
if [ "$matching_containers" -eq "1" ]; then
  echo "Error: container with name $container_name is already running"
  printf "Shut down container? [y/N] "
  read response
  case "$response" in
    y* | Y* )
        docker stop "$container_name" > /dev/null
        ;;
    * )
        echo "Exiting"
        exit 1
        ;;
  esac
fi

# Start fresh container.
echo
echo "start-local-db: Starting postgres container"
echo "-------------------------------------------"

# Note: as of 2023-04-01, Amazon Aurora's latest compatible PG version was 14.6 so
# that's what we use here.
container_id=$(
    docker run \
    --name ${container_name} \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -d --rm \
    -p 6543:5432 \
    postgres:14.6
)
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
