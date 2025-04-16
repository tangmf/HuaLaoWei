#!/bin/bash

ENV=${ENV:-development}
DB_NAME=${DB_NAME:-your_db}
DB_USER=${DB_USER:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo "Loading schema for environment: $ENV"

psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f database/init.sql

if [[ "$ENV" == "development" ]]; then
    echo "Loading dev-only mock data..."
    for f in database/seed/mock/*.sql; do
        echo "$f"
        psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$f"
    done
else
    echo "Skipping mock seeds in $ENV environment"
fi
