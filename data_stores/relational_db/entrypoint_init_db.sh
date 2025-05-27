#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up. Inserting system configuration dynamically..."

echo "Creating extensions..."
for sql_file in /app/data_stores/relational_db/schema/extensions/*.sql; do
  echo "Running $sql_file"
  PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -f "$sql_file"
done

echo "Creating tables..."
for sql_file in /app/data_stores/relational_db/schema/tables/*.sql; do
  echo "Running $sql_file"
  PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -f "$sql_file"
done

echo "Creating functions..."
for sql_file in /app/data_stores/relational_db/schema/functions/*.sql; do
  echo "Running $sql_file"
  PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -f "$sql_file"
done

echo "Creating triggers..."
for sql_file in /app/data_stores/relational_db/schema/triggers/*.sql; do
  echo "Running $sql_file"
  PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -f "$sql_file"
done

echo "Setting system configurations..."
PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c "
INSERT INTO system_config (key, value) VALUES
  ('webhook.issue.url', '$WEBHOOK_ISSUE_URL')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
"

echo "Seeding reference data..."
for ref_file in /app/data_stores/relational_db/seed/reference/*.sql; do
  echo "Running $ref_file"
  PGPASSWORD=$POSTGRES_PASSWORD psql -v ON_ERROR_STOP=1 -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -f "$ref_file"
done

echo "Generating mock data with Python..."
for py_file in /app/data_stores/relational_db/seed/mock/*.py; do
  module_path=$(echo "$py_file" | sed 's|.*/data_stores/relational_db/||' | sed 's|/|.|g' | sed 's|.py$||')
  echo "Running module $module_path"
  python3 -m "$module_path"
done

echo "Database initialization completed successfully."
