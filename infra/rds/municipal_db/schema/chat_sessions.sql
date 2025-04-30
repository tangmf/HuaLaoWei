CREATE TABLE chat_sessions (
    chat_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),                      -- nullable if anonymous
    session_id UUID NOT NULL,                                       -- groups messages into a session
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
    message TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',                        -- e.g. 'text', 'image', 'map'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB                                                  -- optional: NER, intent, etc.
);
