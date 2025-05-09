CREATE TABLE IF NOT EXISTS authorities (
    authority_id SERIAL PRIMARY KEY,
    authority_type VARCHAR(50) NOT NULL CHECK (authority_type IN ('agency', 'town_council')),
    authority_ref_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    UNIQUE(authority_type, authority_ref_id),
    UNIQUE(name, authority_type)
);
