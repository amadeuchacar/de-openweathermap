CREATE TABLE IF NOT EXISTS public.weather_prediction (
    forecast_datetime timestamp NOT NULL,
    city_key varchar(30) NOT NULL,
    weather_parameter varchar(15),
    temperature_celsius double precision,
    humidity_percentage double precision,
    wind_speed_meter_per_sec double precision,
    cloudiness_percentage double precision,
    probability_of_precipitation double precision,
    rain_volume_last_3h_mm double precision,
    wind_direction varchar(10)
);