CREATE TABLE IF NOT EXISTS post_votes (
    user_id INTEGER REFERENCES users(user_id),
    post_id INTEGER REFERENCES forum_posts(post_id),
    vote_type SMALLINT CHECK (vote_type IN (-1, 1)), -- -1 for dislike, 1 for like
    PRIMARY KEY (user_id, post_id)
);

CREATE TABLE IF NOT EXISTS comment_votes (
    user_id INTEGER REFERENCES users(user_id),
    comment_id INTEGER REFERENCES comments(comment_id),
    vote_type SMALLINT CHECK (vote_type IN (-1, 1)),
    PRIMARY KEY (user_id, comment_id)
);
