#!/bin/bash
set -e

# Heroku uses an old URI style that we have to fix.
old="postgres://"
new="postgresql://"
db_url="${DATABASE_URL/"$old"/"$new"}"

here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
seed_files="$here/seeds/*.py"
for file in $seed_files; do
    python $file
done
