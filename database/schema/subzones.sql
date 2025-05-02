CREATE TABLE subzones (
    subzone_id SERIAL PRIMARY KEY,
    planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
    name VARCHAR(100) NOT NULL,
    geom GEOGRAPHY(MULTIPOLYGON, 4326),
    area_sq_m DOUBLE PRECISION
);
