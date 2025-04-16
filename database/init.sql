-- database/init.sql

-- 1. Create schema
\i schema/users.sql
\i schema/agencies.sql
\i schema/town_councils.sql
\i schema/issue_types.sql
\i schema/issue_subcategories.sql
\i schema/issues.sql
-- (Add remaining schemas here)

-- 2. Functions & Procedures
\i functions/aggregate_by_issuetype.sql
\i procedures/refresh_materialised_views.sql

-- 3. Reference Seeds
\i seed/reference/seed_agencies.sql
\i seed/reference/seed_town_councils.sql
\i seed/reference/seed_issue_types.sql
\i seed/reference/seed_issue_subcategories.sql

-- 4. Mock Seeds (optional: uncomment if in dev)
-- \i seed/mock/seed_sample_issues_singapore.sql
