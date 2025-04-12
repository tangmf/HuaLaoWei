CREATE TABLE agencies (
    agency_id SERIAL PRIMARY KEY,
    agency_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
