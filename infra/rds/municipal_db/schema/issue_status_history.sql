CREATE TABLE issue_status_history (
    history_id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT -- optional admin notes
);
