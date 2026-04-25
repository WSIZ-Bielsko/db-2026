alter table messages add constraint fk_sender  foreign key(sender_key)
    references users(pub_key) on delete cascade;

alter table messages add constraint fk_rec foreign key (recipient_key)
references users(pub_key) on delete cascade;
