import boto3
from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator

# Default args to DAG
default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'retries': 0,
}

# Variables
bucket_name = 'openweather-amadeu'
cluster_identifier = 'redshift-cluster-1'
database_name = 'dev'
region = 'us-east-1'
schema = 'public'
tables = ['weather_prediction', 'dim_time', 'dim_city']

def fetch_script(s3_key):
    s3_client = boto3.client('s3')
    s3_key = s3_key

    script_content = s3_client.get_object(Bucket=bucket_name, Key=s3_key)['Body'].read().decode('utf-8')

    return script_content

with DAG(
    dag_id = '02_create_tables_dag',
    description = 'Upload scripts to s3 and create tables in Redshift cluster',
    schedule_interval = None,
    default_args = default_args,
    dagrun_timeout = timedelta(15),
    start_date = days_ago(1)
) as dag:
    
    # TASK 01 - DROP TABLES IF EXIST
    drop_tables_tasks = []
    for table in tables:
        drop_tables = RedshiftDataOperator(
            task_id = f'drop_table_{table}',
            sql = f'DROP TABLE IF EXISTS {schema}.{table}',
            cluster_identifier = cluster_identifier,
            database = database_name,
            wait_for_completion = True,
            region = region
        )
        drop_tables_tasks.append(drop_tables)
        
    sql_script = fetch_script('scripts/sql/create_tables.sql')
    # TASK 02 - CREATE TABLES
    create_tables = RedshiftDataOperator(
        task_id = 'create_tables',
        sql = sql_script,
        cluster_identifier = cluster_identifier,
        database = database_name,
        wait_for_completion = True,
        region = region
    )
    
    drop_tables_tasks >> create_tables