docker compose up airflow-init
rm .env
echo -e "AIRFLOW_UID=$(id -u)" > .env