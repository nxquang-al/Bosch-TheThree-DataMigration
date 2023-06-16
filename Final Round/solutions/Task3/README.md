Initialize Docker
```bash
docker compose up airflow-init
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Run Docker
```bash
docker compose up
```

Clean up
```bash
docker compose down --volumes --rmi all
```