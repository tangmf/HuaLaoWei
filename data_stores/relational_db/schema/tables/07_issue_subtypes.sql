CREATE TABLE IF NOT EXISTS issue_subtypes (
    issue_subtype_id SERIAL PRIMARY KEY,
    issue_type_id INTEGER REFERENCES issue_types(issue_type_id) ON DELETE CASCADE,
    name VARCHAR(150) UNIQUE NOT NULL,
    description TEXT
);
