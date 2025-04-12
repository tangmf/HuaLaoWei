CREATE TABLE media_assets (
    media_id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(issue_id),
    media_type VARCHAR(20) CHECK (media_type IN ('image', 'video', 'audio')),
    file_path TEXT NOT NULL, -- Cloud Object Storage path
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Store image resolution, length, size etc.
);
