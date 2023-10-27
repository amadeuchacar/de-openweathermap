SELECT
    weather_prediction.*,
    dim_time.day_of_week AS day_of_week,
    dim_city.city_name AS city_name
FROM weather_prediction
LEFT JOIN dim_city ON weather_prediction.city_key = dim_city.city_key
LEFT JOIN dim_time ON weather_prediction.forecast_datetime = dim_time.forecast_datetime;