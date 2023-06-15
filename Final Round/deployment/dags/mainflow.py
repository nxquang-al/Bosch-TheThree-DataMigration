
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
from thethree import load_reqif, load_config, build_json, build_rst

log = logging.getLogger(__name__)


def load_reqif_task(**context):
    reqif_filepath = context['dag_run'].conf.get('reqif_filepath')

    log.info(f'Loading reqif from {reqif_filepath}')
    reqif = load_reqif(reqif_filepath)

    context['ti'].xcom_push(key='reqif', value=reqif)


def load_config_then_build_json_task(**context):
    reqif = context['ti'].xcom_pull(key='reqif')
    config_filepath = context['dag_run'].conf.get('config_filepath')

    log.info(f'Loading config from {config_filepath}')
    config = load_config(config_filepath)
    json_data = build_json(reqif, config)

    context['ti'].xcom_push(key='json_data', value=json_data)


def build_rst_task(**context):
    json_data = context['ti'].xcom_pull(key='json_data')
    config_filepath = context['dag_run'].conf.get('config_filepath')

    log.info(f'Loading config from {config_filepath}')
    config = load_config(config_filepath)
    log.info(f'Building rst...')
    build_rst(json_data, config, 'rst_filepath')

    context['ti'].xcom_push(key='rst_filepath', value='')


def upload_to_github_task(**context):
    rst_filepath = context['ti'].xcom_pull(key='rst_filepath')


def update_index_rst_task(**context):
    rst_filepath = context['ti'].xcom_pull(key='rst_filepath')


default_args = {
    "owner": "The Three",
    "depends_on_past": False,
    "retries": None
}

with DAG(
    dag_id="TheThree_reqif_to_rst",
    default_args=default_args,
    description="TheThree Reqif to Rst DAG",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=["reqif", "rst", "TheThree", "Bosch"],
) as dag:
    t1 = PythonOperator(
        task_id="load_reqif",
        python_callable=load_reqif_task,
    )

    t2 = PythonOperator(
        task_id="load_config_then_build_json",
        depends_on_past=True,
        python_callable=load_config_then_build_json_task,
    )

    t3 = PythonOperator(
        task_id="build_rst",
        python_callable=build_rst_task
    )

    t4 = PythonOperator(
        task_id="upload_to_github",
        python_callable=upload_to_github_task
    )

    t5 = PythonOperator(
        task_id="update_index_rst",
        python_callable=update_index_rst_task
    )

    t1 >> t2 >> t3 >> t4 >> t5
