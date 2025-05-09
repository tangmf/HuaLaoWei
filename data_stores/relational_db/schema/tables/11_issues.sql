CREATE TABLE IF NOT EXISTS issues (
    issue_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),

    -- Location Info
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location geography(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    ) STORED,
    address TEXT,

    -- Description & Classification
    description TEXT,
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Reported',
    datetime_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datetime_acknowledged TIMESTAMP,
    datetime_closed TIMESTAMP,
    datetime_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Jurisdiction Info
    authority_id INTEGER REFERENCES authorities(authority_id),

    -- Spatial Context (linked for fast spatial queries)
    planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
    subzone_id INTEGER REFERENCES subzones(subzone_id),

    -- Visibility
    is_public BOOLEAN DEFAULT TRUE,

    -- Triggers
    is_deleted BOOLEAN DEFAULT FALSE
);
