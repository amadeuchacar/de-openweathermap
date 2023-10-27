from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'retries': 0,
}

# Variables
bucket_name = 'openweather-amadeu'
schema = 'public'
tables = ['weather_prediction', 'dim_time', 'dim_city']

with DAG(
    dag_id = '03_load_data_dag',
    description = 'Upload data from s3 to tables in Redshift cluster',
    schedule_interval = None,
    default_args = default_args,
    dagrun_timeout = timedelta(minutes=15),
    start_date = days_ago(1)
) as dag:
    
    load_tables = []
    for table in tables:
        load_data = S3ToRedshiftOperator(
            task_id = f'{table}_load_data',
            redshift_conn_id = 'redshift_conn',
            s3_bucket=bucket_name,
            s3_key=f'gold/parquet/{table}/',
            schema=schema,
            table=table,
            copy_options=["parquet"],
        )
        load_tables.append(load_data)
        
    for i in range(len(load_tables) - 1):
        load_tables[i] >> load_tables[i + 1]