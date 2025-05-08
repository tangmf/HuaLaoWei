CREATE TABLE IF NOT EXISTS issue_media_assets (
    issue_media_id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE,
    media_type VARCHAR(20) CHECK (media_type IN ('image', 'video', 'audio', 'document')),
    file_path TEXT NOT NULL, 
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Optional: dimensions, duration, size, MIME type, etc.
);
