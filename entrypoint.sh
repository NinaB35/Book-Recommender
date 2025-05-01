#!/bin/sh
set -e

alembic upgrade head

echo "Migrations done"

exec "$@"
