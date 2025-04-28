from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
}

# Shared environment variables and mounts
docker_env = {
    'DBT_PROFILES_DIR': '/dbt',
    'POSTGRES_HOST': 'twitter_etl_postgres',
    'POSTGRES_PORT': '5432',
    'POSTGRES_USER': 'twitter',
    'POSTGRES_PASSWORD': 'twitterpass',
    'POSTGRES_DB': 'twitter_etl',
}

docker_mounts = [
    {
        'source': 'D:\\X-pipline\\dbt',
        'target': '/dbt',
        'type': 'bind',
    },
]

# Common DockerOperator parameters
docker_operator_params = {
    'image': 'ghcr.io/dbt-labs/dbt-postgres:latest',
    'api_version': 'auto',
    'auto_remove': True,
    'docker_url': 'unix://var/run/docker.sock',
    'network_mode': 'etl_net',
    'mount_tmp_dir': False,
    'mounts': docker_mounts,
    'environment': docker_env,
}

with DAG(
    'dbt_twitter_etl',
    default_args=default_args,
    description='Run dbt transformations for Twitter ETL',
    schedule_interval=None,
    start_date=datetime(2025, 4, 28),
    catchup=False,
) as dag:

    # Task for stg_twitter_data
    dbt_stg_twitter_data = DockerOperator(
        task_id='dbt_stg_twitter_data',
        command='run --profiles-dir /dbt --project-dir /dbt --models stg_twitter_data --log-level debug',
        **docker_operator_params
    )

    # Task for mart_tweet_count_per_hour
    dbt_mart_tweet_count_per_hour = DockerOperator(
        task_id='dbt_mart_tweet_count_per_hour',
        command='run --profiles-dir /dbt --project-dir /dbt --models mart_tweet_count_per_hour --log-level debug',
        **docker_operator_params
    )

    # Setting up task dependencies
    dbt_stg_twitter_data >> dbt_mart_tweet_count_per_hour
