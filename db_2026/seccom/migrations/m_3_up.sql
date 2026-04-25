alter table group_users add constraint fk_user foreign key(user_key)
    references users(pub_key) on delete cascade;