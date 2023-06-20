from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import os
from thethree import *

log = logging.getLogger(__name__)


def load_reqif_and_configs_task(**context):
    default_reqif_file_path = "/opt/airflow/config/ECU_Requirement.reqif"
    default_mapping_config_file_path = "/opt/airflow/config/mapping_config.yaml"
    default_github_config_file_path = "/opt/airflow/config/github_config.yaml"

    reqif_file_path = context['dag_run'].conf.get(
        'reqif_file_path', default_reqif_file_path)
    mapping_config_file_path = context['dag_run'].conf.get(
        'mapping_config_file_path', default_mapping_config_file_path)
    github_config_file_path = context['dag_run'].conf.get(
        'github_config_file_path', default_github_config_file_path)

    reqif_file = context['dag_run'].conf.get('reqif_file', None)
    mapping_config_file = context['dag_run'].conf.get(
        'mapping_config_file', None)
    github_config_file = context['dag_run'].conf.get(
        'github_config_file', None)

    reqif = reqif_file if reqif_file is not None else load_reqif(
        reqif_file_path)
    mapping_config = mapping_config_file if mapping_config_file is not None else load_config(
        mapping_config_file_path)
    github_config = github_config_file if github_config_file is not None else load_config(
        github_config_file_path)

    reqif_file_name = os.path.basename(reqif_file_path)
    rst_file_name = reqif_file_name.replace(".reqif", ".rst")
    rst_file_path = f"docs/src/{rst_file_name}"

    context['ti'].xcom_push(key='reqif', value=reqif)
    context['ti'].xcom_push(key='mapping_config', value=mapping_config)
    context['ti'].xcom_push(key='github_config', value=github_config)
    context['ti'].xcom_push(key='rst_file_path', value=rst_file_path)


def build_json_task(**context):
    reqif = context['ti'].xcom_pull(key='reqif')
    mapping_config = context['ti'].xcom_pull(key='mapping_config')

    json_data = build_json(reqif, mapping_config)

    context['ti'].xcom_push(key='json_data', value=json_data)


def build_rst_task(**context):
    json_data = context['ti'].xcom_pull(key='json_data')
    mapping_config = context['ti'].xcom_pull(key='mapping_config')

    rst_data = build_rst(json_data, mapping_config)

    context['ti'].xcom_push(key='rst_data', value=rst_data)


def upload_to_github_task(**context):
    rst_data = context['ti'].xcom_pull(key='rst_data')
    rst_file_path = context['ti'].xcom_pull(key='rst_file_path')
    github_config = context['ti'].xcom_pull(key='github_config')

    upload_to_github(github_config, rst_file_path, rst_data)


def update_index_rst_task(**context):
    json_data = context['ti'].xcom_pull(key='json_data')
    mapping_config = context['ti'].xcom_pull(key='mapping_config')
    github_config = context['ti'].xcom_pull(key='github_config')
    rst_file_path = context['ti'].xcom_pull(key='rst_file_path')

    module_type = json_data[mapping_config['module']['type']['key']]
    update_index_rst(github_config, rst_file_path, module_type)


default_args = {
    "owner": "The Three",
    "depends_on_past": False,
    "retries": 5
}

with DAG(
    dag_id="thethree_reqif_to_rst",
    default_args=default_args,
    description="TheThree Reqif to Rst DAG",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=["reqif", "rst", "TheThree", "Bosch"],
) as dag:
    t1 = PythonOperator(
        task_id="load_reqif_and_configs",
        python_callable=load_reqif_and_configs_task,
    )

    t2 = PythonOperator(
        task_id="build_json",
        python_callable=build_json_task,
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
