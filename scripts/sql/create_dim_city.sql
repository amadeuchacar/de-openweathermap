CREATE TABLE IF NOT EXISTS public.dim_city (
    city_key varchar(30) NOT NULL,
    city_name varchar(60),
    city_latitude double precision,
    city_longitude double precision,
    country varchar(10),
    timezone_from_utc double precision
);