#!/bin/bash

# Usage:
#   ENV=development ./load_sql_seeds.sh
#   ENV=production ./load_sql_seeds.sh

# Database credentials
DB_NAME=${DB_NAME:-your_db_name}
DB_USER=${DB_USER:-your_db_user}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

# Set environment (default = development)
ENV=${ENV:-development}

echo "Environment: $ENV"
echo "Loading reference data..."

for file in ./db_schema/reference/*.sql; do
    echo "📄 Executing $file"
    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file"
done

if [[ "$ENV" == "development" ]]; then
    echo "🌱 Loading mock data..."
    for file in ./db_schema/mock/*.sql; do
        echo "📄 Executing $file"
        psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file"
    done
else
    echo "🚫 Skipping mock data in non-development environment."
fi

echo "✅ Seed loading complete."
