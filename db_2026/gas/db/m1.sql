create schema if not exists xxx;
set search_path to xxx;

set search_path to public;

CREATE TABLE fuel_type (
    id SERIAL PRIMARY KEY,
    name text NOT NULL UNIQUE
);

CREATE TABLE gas_station (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    city text NOT NULL,
    address text NOT NULL,
    x numeric(8,6) NOT NULL,
    y numeric(9,6) NOT NULL
);

CREATE TABLE fuel_offers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    price_per_liter numeric(4, 2),
    station_id uuid NOT NULL,
    posted_at timestamp NOT NULL ,
    fuel_type_id integer NOT NULL,
    CONSTRAINT fk_fuel_offers_station FOREIGN KEY (station_id) REFERENCES gas_station(id) ON DELETE CASCADE,
    CONSTRAINT fk_fuel_offers_fuel_type FOREIGN KEY (fuel_type_id) REFERENCES fuel_type(id) ON DELETE CASCADE
);

drop schema xxx cascade ;