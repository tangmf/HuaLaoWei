CREATE TABLE town_councils (
    town_council_id SERIAL PRIMARY KEY,
    council_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
