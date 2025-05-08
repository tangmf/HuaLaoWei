CREATE TABLE IF NOT EXISTS subzones (
    subzone_id SERIAL PRIMARY KEY,
    planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
    name VARCHAR(100) UNIQUE NOT NULL,
    geom GEOGRAPHY(MULTIPOLYGON, 4326),
    area_sq_m double precision GENERATED ALWAYS AS (ST_Area(geom::geography)) STORED
);
