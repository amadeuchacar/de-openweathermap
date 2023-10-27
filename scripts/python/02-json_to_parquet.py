from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
import boto3
import logging

logging.basicConfig(level=logging.INFO)

spark = SparkSession.builder \
                    .appName("Json_To_Parquet") \
                    .getOrCreate()
                    
spark._jsc.hadoopConfiguration().set("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

s3_client = boto3.client('s3')

def preprocessingJson(df):
    logging.info('-- Iniciando o pré processamento do JSON.....')
    exploded_df = df.select(
        col('city.coord.lat').alias('latitude'),
        col('city.coord.lon').alias('longitude'),
        col('city.country').alias('country'),
        col('city.id').alias('city_id'),
        col('city.name').alias('city_name'),
        col('city.sunrise').alias('sunrise'),
        col('city.sunset').alias('sunset'),
        col('city.timezone').alias('timezone'),
        col('cnt'),
        col('cod'),
        col('message'),
        explode(col('list')).alias('exploded_list')
    )

    exploded_df = exploded_df.select(
        col('latitude'),
        col('longitude'),
        col('country'),
        col('city_id'),
        col('city_name'),
        col('sunrise'),
        col('sunset'),
        col('timezone'),
        col('cnt'),
        col('cod'),
        col('message'),
        col('exploded_list.dt').alias('dt'),
        col('exploded_list.main.temp').alias('main_temp'),
        col('exploded_list.main.feels_like').alias('main_feels_like'),
        col('exploded_list.main.temp_min').alias('main_temp_min'),
        col('exploded_list.main.temp_max').alias('main_temp_max'),
        col('exploded_list.main.pressure').alias('main_pressure'),
        col('exploded_list.main.sea_level').alias('main_sea_level'),
        col('exploded_list.main.grnd_level').alias('main_grnd_level'),
        col('exploded_list.main.humidity').alias('main_humidity'),
        col('exploded_list.main.temp_kf').alias('main_temp_kf'),
        explode(col('exploded_list.weather')).alias('weather'),
        col('exploded_list.clouds.all').alias('clouds_all'),
        col('exploded_list.wind.speed').alias('wind_speed'),
        col('exploded_list.wind.deg').alias('wind_deg'),
        col('exploded_list.wind.gust').alias('wind_gust'),
        col('exploded_list.visibility').alias('visibility'),
        col('exploded_list.pop').alias('pop'),
        col('exploded_list.sys.pod').alias('sys_pod'),
        col('exploded_list.dt_txt').alias('dt_txt'),
        col('exploded_list.rain.3h').alias('rain_3h')
    )

    exploded_df = exploded_df.select(
        col('latitude'),
        col('longitude'),
        col('country'),
        col('city_id'),
        col('city_name'),
        col('sunrise'),
        col('sunset'),
        col('timezone'),
        col('cnt'),
        col('cod'),
        col('message'),
        col('dt'),
        col('main_temp'),
        col('main_feels_like'),
        col('main_temp_min'),
        col('main_temp_max'),
        col('main_pressure'),
        col('main_sea_level'),
        col('main_grnd_level'),
        col('main_humidity'),
        col('main_temp_kf'),
        col('weather.description').alias('weather_description'),
        col('weather.icon').alias('weather_icon'),
        col('weather.id').alias('weather_id'),
        col('weather.main').alias('wather_main'),
        col('clouds_all'),
        col('wind_speed'),
        col('wind_deg'),
        col('wind_gust'),
        col('visibility'),
        col('pop'),
        col('sys_pod'),
        col('dt_txt'),
        col('rain_3h')
    )
    
    logging.info('-- Pré processamento do JSON terminado!')
    return exploded_df


if __name__ == '__main__':
    bucket_name = 'openweather-amadeu'
    prefix = 'raw/landing/json/'
    s3_objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    s3_files = s3_objects.get("Contents")
    s3_file_names = []
    
    logging.info('-- Buscando arquivos existentes no bucket....')
    
    for file in s3_files:
        file_name = file['Key']
        if file_name != prefix:
            s3_file_names.append(file_name)
        
    n_files = len(s3_file_names)
    logging.info(f'-- Encontrados {n_files} arquivos!')
        
    for file in s3_file_names:
        layer, state, format_file, file_name_format = file.split("/")
        file_name, extension = file_name_format.split(".")
        dst_processed_path = f'raw/processed/json/{file_name_format}'
        dst_final_path = f's3a://{bucket_name}/bronze/parquet/{file_name}'
        
        logging.info(f'-- Lendo arquivo {file}....')
        bckt_path = f's3a://{bucket_name}/{file}'
        
        df = spark.read \
                .option("inferSchema", "true") \
                .option("multiLine", "true") \
                .json(bckt_path)

        df_processed = preprocessingJson(df)

        logging.info(f'-- Salvando arquivo {file} processado....')
        df_processed.write.mode("overwrite").parquet(dst_final_path)


        logging.info(f'-- Movendo arquivo {file} da landing para processed....')
        s3_client.copy_object(
            Bucket = bucket_name, 
            CopySource = {
                'Bucket': bucket_name, 
                'Key': file}, 
            Key = dst_processed_path
        )
        
        s3_client.delete_object(Bucket=bucket_name, Key=file)
        s3_client.delete_object(Bucket=bucket_name, Key=f'bronze/parquet/{file_name}/_SUCESS')