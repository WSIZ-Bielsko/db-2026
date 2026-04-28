alter table invites
    alter column challenge type uuid using challenge::uuid;