# Relational Database (PostgreSQL)

This folder contains all the setup scripts and seeders for the **PostgreSQL** relational database.

## Components

- `Dockerfile.postgres`  
  Custom PostgreSQL image that installs additional tools like Python 3, pip, and required libraries.
- `Dockerfile.init_postgres`  
  Lightweight container to run database initialization scripts automatically.
- `setup.sh`  
  Shell script that creates tables, sets up functions and triggers, and seeds initial data (both reference and mock).

## Schema and Seeding

- `schema/`  
  Contains SQL files defining all tables, indexes, functions, and triggers.
- `seed/reference/`  
  Contains SQL files for seeding static reference data.
- `seed/mock/`  
  Contains Python scripts that generate dynamic mock data (e.g., users, issues).

## Usage

1. Build and run `postgres` service using Docker Compose.
2. Build and run `init_postgres` service to automatically setup schema and seed data.

```bash
make setup-dev
make up