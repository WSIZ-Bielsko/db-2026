create table invites(
    invite_id UUID not null,
    challenge UUID
);

-- no uniqueness -> many tokens per user (multiple devices; stored in localstorage)
create table users (
    pub_key text primary key,
    token text
);