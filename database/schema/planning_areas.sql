CREATE TABLE planning_areas (
    planning_area_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    geom GEOGRAPHY(MULTIPOLYGON, 4326) -- Optional: entire area boundary
);
