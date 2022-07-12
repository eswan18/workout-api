docker run \
    --name workout-api-postgres \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -d --rm \
    -p 6543:5432 \
    postgres:14
