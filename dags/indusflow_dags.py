from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "indusflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}


with DAG(
    dag_id="indusflow_pipeline",
    default_args=default_args,
    description="Pipeline Data Engineering IndusFlow",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:


    # Etape 1 : Nettoyage des fichiers CSV
    clean_data = BashOperator(
        task_id="clean_data",
        bash_command="""
        cd /opt/airflow
        python3 /opt/airflow/etl/etl_python.py
        """
    )


    # Etape 2 : Chargement PostgreSQL
    load_postgresql = BashOperator(
        task_id="load_postgresql",
        bash_command="""
        cd /opt/airflow
        python3 /opt/airflow/etl/etl_postgresql.py
        """
    )


    # Etape 3 : Calcul KPI
    generate_kpi = BashOperator(
        task_id="generate_kpi",
        bash_command="""
        cd /opt/airflow
        python3 /opt/airflow/kpi_postgresql.py
        """
    )


    clean_data >> load_postgresql >> generate_kpi
