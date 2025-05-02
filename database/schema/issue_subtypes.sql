CREATE TABLE issue_subtypes (
    subtype_id SERIAL PRIMARY KEY,
    issue_type_id INTEGER REFERENCES issue_types(issue_type_id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    description TEXT
);
