#!/bin/bash

here=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
psql $DATABASE_URL -f $here/seeds/*
