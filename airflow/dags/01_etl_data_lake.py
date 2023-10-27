from datetime import timedelta
import boto3
import os

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

# Default args to DAG
default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'retries': 0,
}

# Variables
bucket_name = 'openweather-amadeu'
cluster_identifier = 'redshift-cluster-1'
iam_role = 's3gluefullaccessTerraform'
region_name = 'us-east-1'

# Python function to upload scripts to s3
def upload_scripts_to_s3():
    s3_client = boto3.client('s3')
    type_script = ['python', 'sql']
    
    for type_script in type_script:
        list_scripts = os.listdir(f'/opt/scripts/{type_script}')
        for file in list_scripts:
            s3_client.upload_file(
                Bucket = bucket_name,
                Filename = f'/opt/scripts/{type_script}/{file}',
                Key = f'scripts/{type_script}/{file}'
            )

# Python function to list the scripts in s3
def list_scripts():
    s3_client = boto3.client('s3')
    directory_prefix = 'scripts/python'
    
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory_prefix)
    
    list_scripts_s3 = []
    count = 0
    if 'Contents' in response:
        for script in response['Contents']:
            if count > 0:
                obj = script['Key']
                list_scripts_s3.append(obj)
            count += 1
            
    return list_scripts_s3

# ETL OPENWEATHER DAG
with DAG(
    dag_id = '01_etl_data_lake',
    description = 'Data Lake ETL process',
    schedule_interval = timedelta(hours=1),
    start_date = days_ago(1),
    default_args = default_args,
    catchup = False
) as dag:
    
    # TASK 01 - INGESTION
    ingestion = BashOperator(
        task_id = 'ingestion_datalake',
        bash_command = 'python /opt/scripts/python/01-coleta_dados.py',
        dag = dag
    )
    
    try:
        # TASKS ETL RAW -> BRONZE -> SILVER -> GOLD
        scripts = list_scripts()
        etl_tasks = []
        count = 0
        for script in scripts:
            if script != 'scripts/python/01-coleta_dados.py':
                count = count + 1
                
                etl_step = GlueJobOperator(
                    task_id = f'etl_step_{count}',
                    job_name = f'etl_step_{count}',
                    script_location = f's3://{bucket_name}/{script}',
                    iam_role_name = iam_role,
                    region_name = region_name,
                    create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X", "Timeout": 15, "MaxRetries": 2}
                )
                
                etl_tasks.append(etl_step)

        ingestion >> etl_tasks[0]

        for i in range(len(etl_tasks) - 1):
            etl_tasks[i] >> etl_tasks[i + 1]
    except:
        ingestion