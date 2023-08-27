#!/bin/bash

echo "Creating views..."

# For each sql file in this folder, create a view in the database
here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
view_files="$here/views/*.sql"
for file in $view_files; do
    echo "Running $file"
    psql "$DATABASE_URL" -f $file
done