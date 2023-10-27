from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, col
import boto3
import logging

logging.basicConfig(level=logging.INFO)

spark = SparkSession.builder \
                    .appName("Json_To_Parquet") \
                    .getOrCreate()
                    
spark._jsc.hadoopConfiguration().set("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

s3_client = boto3.client('s3')

def create_city_key(df):
    df = df.withColumn(
        "city_key",
        concat(col("city_latitude"), col("city_longitude"), col("country"))
    )

    return df

def create_fact_table(df):
    df = df.select(
        "forecast_datetime",
        "city_key",
        "weather_parameter",
        "temperature_celsius",
        "humidity_percentage",
        "wind_speed_meter_per_sec",
        "cloudiness_percentage",
        "probability_of_precipitation",
        "rain_volume_last_3h_mm",
        "wind_direction"
    )

    return df

def create_dim_city(df):
    df = df.select(
        "city_key",
        "city_name",
        "city_latitude",
        "city_longitude",
        "country",
        "timezone_from_utc"
    ).distinct()

    return df

def create_dim_time(df):
    df = df.select(
        "forecast_datetime",
        "day_of_week"
    ).distinct()

    return df

if __name__ == '__main__':
    
    bucket_name = 'openweather-amadeu'
    prefix = 'silver/parquet/'
    
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    s3_dir_names = []

    logging.info('-- Buscando arquivos existentes no bucket....')
    
    for common_prefix in response.get('CommonPrefixes', []):
        s3_dir_names.append(common_prefix['Prefix'])
            
    n_files = len(s3_dir_names)
    logging.info(f'-- Encontrados {n_files} arquivos!')

    basePath = f's3a://{bucket_name}/{prefix}'
    logging.info('-- Lendo arquivos....')
    
    silver_df = spark.read.option("mergeSchema", "true").parquet(basePath)
    
    silver_df = create_city_key(silver_df)
    fact_table = create_fact_table(silver_df)
    dim_city = create_dim_city(silver_df)
    dim_time = create_dim_time(silver_df)

    logging.info(f'-- Salvando arquivo processado....')
    dst_final_path = f's3a://{bucket_name}/gold/parquet/'

    try:
        fact_table.write.mode("overwrite").parquet(f"{dst_final_path}/weather_prediction")
        dim_city.write.mode("overwrite").parquet(f"{dst_final_path}/dim_city")
        dim_time.write.mode("overwrite").parquet(f"{dst_final_path}/dim_time")
        
        logging.info(f'Arquivo modelado e salvo com sucesso!')
    except:
        logging.info(f'Não foi possível salvar o arquivo')