alter table invites
    alter column challenge type text using challenge::text;
