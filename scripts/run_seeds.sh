#!/bin/bash

# Heroku uses an old URI style that we have to fix.
old="postgres://"
new="postgresql://"
db_url="${DATABASE_URL/"$old"/"$new"}"

here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
psql $db_url -f $here/seeds/*
