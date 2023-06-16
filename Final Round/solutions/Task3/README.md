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