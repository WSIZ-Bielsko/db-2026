-- Create the groups table first since other tables reference it
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

-- Create the group_users table with a composite primary key
CREATE TABLE group_users (
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_key TEXT NOT NULL,
    PRIMARY KEY (group_id, user_key)
);

-- Create the messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    sender_key TEXT NOT NULL,
    recipient_key TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    group_id UUID REFERENCES groups(id) ON DELETE SET NULL
);