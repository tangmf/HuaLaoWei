CREATE TABLE IF NOT EXISTS planning_areas (
    planning_area_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    geom GEOGRAPHY(MULTIPOLYGON, 4326),
    area_sq_m double precision GENERATED ALWAYS AS (ST_Area(geom::geography)) STORED
);
