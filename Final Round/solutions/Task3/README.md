Trigger Airflow
```json
{
    "reqif_file_path": "/path/to/requirement.reqif",
    "mapping_config_file_path": "/path/to/mapping_config.yml",
    "github_config_file_path": "/path/to/github_config.yml"
}
```

Initialize Docker
```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
```

Run Docker
```bash
docker compose up
```

Clean up
```bash
docker compose down --volumes --rmi all
```