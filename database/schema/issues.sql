CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
    
    -- Location Info
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    full_address TEXT,
    location GEOGRAPHY(Point, 4326),

    -- Description & Classification
    description TEXT,
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Reported',
    datetime_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datetime_acknowledged TIMESTAMP,

    -- Jurisdiction Info
    agency_id INTEGER REFERENCES agencies(agency_id),
    town_council_id INTEGER REFERENCES town_councils(town_council_id),
    
    is_public BOOLEAN DEFAULT TRUE
);
