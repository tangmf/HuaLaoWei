CREATE TABLE IF NOT EXISTS forum_posts (
    post_id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(issue_id),
    user_id INTEGER REFERENCES users(user_id),
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
