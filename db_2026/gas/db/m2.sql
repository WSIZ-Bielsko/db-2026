
--up
alter table xxx.fuel_offers
    alter column price_per_liter set not null;


--down
alter table xxx.fuel_offers
    alter column price_per_liter drop not null;