CREATE TABLE jurisdictions (
    jurisdiction_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    geom GEOGRAPHY(POLYGON, 4326), -- Spatial boundary of the jurisdiction
    town_council_id INTEGER REFERENCES town_councils(town_council_id)
);
