CREATE TABLE forum_posts (
    post_id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(issue_id),
    user_id INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
