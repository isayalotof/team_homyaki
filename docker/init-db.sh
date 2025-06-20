#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE russia_travel_db;
    GRANT ALL PRIVILEGES ON DATABASE russia_travel_db TO postgres;
EOSQL 