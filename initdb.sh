#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
    GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
    \c ${DB_NAME}
    GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};
EOSQL

echo "Created user ${DB_USER}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${TEST_DB_NAME} WITH OWNER ${DB_USER};
EOSQL

echo "Created user ${DB_USER}"
