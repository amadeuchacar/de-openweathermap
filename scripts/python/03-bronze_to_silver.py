from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col, when, dayofweek
import boto3
import logging

logging.basicConfig(level=logging.INFO)

spark = SparkSession.builder \
                    .appName("Json_To_Parquet") \
                    .getOrCreate()
                    
spark._jsc.hadoopConfiguration().set("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

s3_client = boto3.client('s3')

# TRANSFORMATIONS
def selectingColumns(df):
    df = df.select(
        col('dt'),
        col('main_temp').alias('temperature_kelvin'),
        col('main_feels_like').alias('feels_like_temperature_kelvin'),
        col('main_temp_min').alias('minimum_temperature_kelvin'),
        col('main_temp_max').alias('maximum_temperature_kelvin'),
        col('main_pressure').alias('atmospheric_pressure_hpa'),
        col('main_sea_level').alias('atmospheric_pressure_sea_level_hpa'),
        col('main_grnd_level').alias('atmospheric_pressure_ground_level_hpa'),
        col('main_humidity').alias('humidity_percentage'),
        col('wather_main').alias('weather_parameter'),
        col('weather_description').alias('weather_description'),
        col('clouds_all').alias('cloudiness_percentage'),
        col('wind_speed').alias('wind_speed_meter_per_sec'),
        col('wind_deg').alias('wind_direction_degrees'),
        col('wind_gust').alias('wind_gust_meter_per_sec'),
        col('visibility').alias('average_visibility_meters'),
        col('pop').alias('probability_of_precipitation'),
        col('rain_3h').alias('rain_volume_last_3h_mm'),
        col('sys_pod').alias('day_or_night'),
        col('city_id'),
        col('city_name'),
        col('latitude').alias('city_latitude'),
        col('longitude').alias('city_longitude'),
        col('country'),
        col('timezone').alias('timezone_from_utc'),
        col('sunrise'),
        col('sunset')
    )

    return df

def bronzeProcessing(df):
    # Unix time to Timestamp
    df = df.withColumn("forecast_datetime", from_unixtime("dt").cast("timestamp"))
    df = df.drop("dt")
    df = df.withColumn("sunrise_datetime", from_unixtime("sunrise").cast("timestamp"))
    df = df.drop("sunrise")
    df = df.withColumn("sunset_datetime", from_unixtime("sunset").cast("timestamp"))
    df = df.drop("sunset")

    # Timezone from UTC -> seconds to hours
    df = df.withColumn("timezone_from_utc", col("timezone_from_utc") / 3600)
    
    # Kelvin to Celsius
    df = df.withColumn("temperature_celsius", df["temperature_kelvin"] - 273.15)
    df = df.drop('temperature_kelvin')
    df = df.withColumn("feels_like_temperature_celsius", df["feels_like_temperature_kelvin"] - 273.15)
    df = df.drop('feels_like_temperature_kelvin')
    df = df.withColumn("minimum_temperature_celsius", df["minimum_temperature_kelvin"] - 273.15)
    df = df.drop('minimum_temperature_kelvin')
    df = df.withColumn("maximum_temperature_celsius", df["maximum_temperature_kelvin"] - 273.15)
    df = df.drop('maximum_temperature_kelvin')
    
    # Atmospheric pressure -> bigint to double
    df = df.withColumn("atmospheric_pressure_hpa", df["atmospheric_pressure_hpa"].cast("double"))
    
    # Humidity percentage -> bigint (0...100) to double (0, 0.1....1)
    df = df.withColumn("humidity_percentage", df["humidity_percentage"].cast("double") / 100.0)
    
    # Cloudiness percentage -> bigint (0...100) to double (0, 0.1....1)
    df = df.withColumn("cloudiness_percentage", df["cloudiness_percentage"].cast("double") / 100.0)
    
    # Wind directions degree -> bigint to double
    df = df.withColumn("wind_direction_degrees", df["wind_direction_degrees"].cast("double"))
    
    # Rain in the last 3 hours -> null to 0
    df = df.withColumn("rain_volume_last_3h_mm",
                       when(col("rain_volume_last_3h_mm").isNull(), 0.0).otherwise(col("rain_volume_last_3h_mm")))
    
    # Day or Night -> d / n to 'day' or 'night'
    df = df.withColumn("day_or_night", when(col("day_or_night") == "d", "day") \
                                       .when(col("day_or_night") == "n", "night") \
                                       .otherwise(col("day_or_night")))

    # Wind direction degrees -> Wind direction (norte, sul, leste, oeste)
    df = df.withColumn("wind_direction", 
         when((col("wind_direction_degrees") >= 0) & (col("wind_direction_degrees") < 45), "Norte")
        .when((col("wind_direction_degrees") >= 45) & (col("wind_direction_degrees") < 135), "Leste")
        .when((col("wind_direction_degrees") >= 135) & (col("wind_direction_degrees") < 225), "Sul")
        .otherwise("Oeste")
    )
    df = df.drop('wind_direction_degrees')

    # Day of week column
    df = df.withColumn("day_of_week", dayofweek(col("forecast_datetime")))

    # Remove some columns
    df = df.drop('city_id')
    df = df.drop('atmospheric_pressure_sea_level_hpa')
    df = df.drop('atmospheric_pressure_ground_level_hpa')
    df = df.drop('weather_description')
    df = df.drop('sunrise_datetime')
    df = df.drop('sunset_datetime')
    df = df.drop('day_or_night')
    
    logging.info('-- Transformação finalizada!')
    return df
    
if __name__ == '__main__':
    
    bucket_name = 'openweather-amadeu'
    prefix = 'bronze/parquet/'
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    s3_dir_names = []

    logging.info('-- Buscando arquivos existentes no bucket....')

    try:
        for obj in response.get('Contents', []):
            key = obj['Key']
            
            if key.endswith('/'):
                s3_dir_names.append(key)
                
        n_files = len(s3_dir_names)
        logging.info(f'-- Encontrados {n_files} arquivos!')

        basePath = f's3a://{bucket_name}/{prefix}'
        logging.info('-- Lendo arquivos....')
        bronze_data_frame = spark.read.option("basePath", basePath).parquet(basePath + "*/*")

        bronze_data_frame = selectingColumns(bronze_data_frame)
        bronze_data_frame = bronzeProcessing(bronze_data_frame)

        logging.info(f'-- Salvando arquivo processado....')
        dst_final_path = f's3a://{bucket_name}/silver/parquet/'
        bronze_data_frame.write.mode("overwrite").parquet(dst_final_path)
    except:
        logging.info('Não foi encontrado nenhum diretório no bucket S3.')