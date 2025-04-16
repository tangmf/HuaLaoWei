# Database Directory for Smart City Civic Reporting Platform

This directory contains everything related to our database schema, structure and backend logic within our project. 
The database is optimised for use on Huawei Cloud (GaussDB), but is also fully portable for local development and CI pipelines.

---

## Folder Structure

```
database/
├── README.md                          # This file
├── init.sql                           # Master script for schema + seed loading
│
├── schema/                            # All core table definitions
│   ├── users.sql
│   ├── issues.sql
│   ├── issue_types.sql
│   ├── issue_subcategories.sql
│   └── ...
│
├── seed/
│   ├── reference/                     # Production-safe reference data
│   │   ├── seed_agencies.sql
│   │   ├── seed_town_councils.sql
│   │   └── seed_issue_types.sql
│   └── mock/                          # Development/test-only seed data
│       └── seed_sample_issues_singapore.sql
│
├── migrations/                        # Optional: incremental schema changes
│   └── 001_init_schema.sql
│
├── procedures/                        # Stored procedures
│   └── refresh_materialised_views.sql
│
├── functions/                         # User-defined SQL functions
│   └── aggregate_by_issuetype.sql
│
└── diagrams/                          # ER diagrams or visual aids
    └── schema_diagram.png
```

---

## Getting Started

### 1. Local Setup (Manual)

```bash
# Load everything (reference seeds only)
psql -U <user> -d <db> -f database/init.sql

# Optional: Load mock data for testing (dev only)
psql -U <user> -d <db> -f database/seed/mock/seed_sample_issues_singapore.sql
```

### 2. Local Setup (Scripted)

Use the automated script:

```bash
ENV=development ./scripts/run_init.sh
```

This will:
- Load all schema and reference data
- Conditionally load mock data if `ENV=development`

---

## `init.sql`: What It Does

- Loads all table definitions in `schema/`
- Loads all stored `functions/` and `procedures/`
- Loads seed data from `seed/reference/`
- Optional mock data is excluded by default

> Designed to be used in local development, dev containers, and CI pipelines

---

## Schema Highlights

- Modular, relational schema for civic issue reporting
- Location-aware and jurisdictional routing (agency + town council)
- Supports:
  - Public vs private issue visibility
  - Issue lifecycle tracking (reported > acknowledged > closed)
  - Categorisation (type + subcategory based on OneService)
  - Media metadata (e.g., OBS-hosted files)
  - Commenting and voting for public issues
- Compatible with PostGIS (for GEOGRAPHY and jurisdiction matching)

---

## 🔒 Environments

| Environment  | Behavior                         |
|--------------|----------------------------------|
| `production` | Loads schema + reference seeds only |
| `development`| Loads schema + reference + mock seeds |
| `ci/test`    | Configurable depending on pipeline setup |

---

## 🧹 Migration & Version Control

Use `migrations/` to manage schema changes over time.

Naming convention recommended:

```
001_init_schema.sql
002_add_issue_history_table.sql
003_add_foreign_key_fix.sql
...
```

These can be executed manually or with tools like:
- Flyway
- Liquibase
- Prisma Migrate
- Sequelize CLI

---

## Visual Documentation

Place ERD exports or draw.io diagrams in `diagrams/`:

- Use for team onboarding
- Share in presentations or proposals

Recommended filenames:
- `schema_diagram.png`
- `jurisdiction_logic.pdf`

---

## Contributors

- **Project**: National AI Student Challenge 2025 — Local Track 5 (Huawei)

---

## 🔡 License

This schema and setup are intended for **academic, innovation, and public-interest projects**. For commercial use, contact the project owner or maintainers.
```

