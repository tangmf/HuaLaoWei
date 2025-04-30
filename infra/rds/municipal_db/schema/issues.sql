CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),

    issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
    issue_subtype_id INTEGER REFERENCES issue_subtypes(issue_subtype_id),

    -- Location Info
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address TEXT,
    location TEXT,

    -- Description & Classification
    description TEXT,
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Reported',
    datetime_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datetime_acknowledged TIMESTAMP,
    datetime_closed TIMESTAMP,
    datetime_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Jurisdiction Info
    agency_id INTEGER REFERENCES agencies(agency_id),
    town_council_id INTEGER REFERENCES town_councils(town_council_id),

    -- Spatial Context (linked for fast spatial queries)
    planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
    subzone_id INTEGER REFERENCES subzones(subzone_id),

    -- Visibility
    is_public BOOLEAN DEFAULT TRUE,

    -- Triggers
    is_deleted BOOLEAN DEFAULT FALSE
);
