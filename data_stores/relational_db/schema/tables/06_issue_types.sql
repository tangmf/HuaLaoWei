CREATE TABLE IF NOT EXISTS issue_types (
    issue_type_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
