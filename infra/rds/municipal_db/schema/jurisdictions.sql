/*
This table represents spatial areas (e.g., HDB estate, precinct, town), which can be used to route issues based on geography.
*/
CREATE TABLE jurisdictions (
    jurisdiction_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    -- geom GEOGRAPHY(POLYGON, 4326), -- Spatial boundary of the jurisdiction
    town_council_id INTEGER REFERENCES town_councils(town_council_id)
);
