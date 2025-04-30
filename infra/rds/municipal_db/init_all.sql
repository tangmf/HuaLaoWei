/* 
    init_all.sql:
    
    This script initializes the municipal database by creating the necessary schemas and tables.
    It also seeds the database with reference data for users, agencies, issue types, and planning areas.
*/

-- 
-- DB SETUP
--


--
-- SCHEMA CREATION
--
-- User and governing body
\i schema/users.sql
\i schema/agencies.sql
\i schema/town_councils.sql

-- Regional planning areas and subzones
\i schema/planning_areas.sql
\i schema/subzones.sql

-- Issue definitions
\i schema/issue_types.sql
\i schema/issue_subtypes.sql
\i schema/jurisdictions.sql
\i schema/issue_type_mappings.sql

-- Core issues tables that references the above
\i schema/issues.sql
\i schema/issue_status_history.sql

-- Related media/forum/comment tables
\i schema/media_assets.sql
\i schema/forum_posts.sql
\i schema/comments.sql
\i schema/votes.sql

-- Chatbot
\i schema/chat_sessions.sql

--
-- SEEDING DATA
--
-- Seed reference files
\i seed/reference/seed_agencies.sql
\i seed/reference/seed_town_councils.sql
\i seed/reference/seed_planning_areas.sql
\i seed/reference/seed_subzones.sql
\i seed/reference/seed_issue_types.sql
\i seed/reference/seed_issue_subtypes.sql