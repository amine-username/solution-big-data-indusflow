import pandas as pd
from sqlalchemy import create_engine
import os


# Connexion PostgreSQL Docker

engine = create_engine(
    "postgresql://indusflow_user:indusflow_password@localhost:5432/indusflow"
)


folder = "../data_clean"


mapping_tables = {

    "cycles_production_bloc3_propre.csv": "cycles_production",

    "cameras_qualite_bloc3_propre.csv": "cameras_qualite",

    "maintenance_machines_bloc3_propre.csv": "maintenance_machines",

    "logs_erreurs_machines_bloc3_propre.csv": "logs_erreurs_machines",

    "capteurs_machines_bloc3_propre.csv": "capteurs_machines",

    "planning_production_bloc3_propre.csv": "planning_production",
    "logs_jobs_airflow.csv": "logs_jobs_airflow",
    "alertes_monitoring.csv": "alertes_monitoring",
    "usines_bloc3_propre.csv": "usines"


}


for file, table in mapping_tables.items():

    path = folder + "/" + file

    if os.path.exists(path):

        print("Chargement :", file)

        df = pd.read_csv(path)

        df.to_sql(
            table,
            engine,
            if_exists="replace",
            index=False
        )

        print(
            table,
            "OK - lignes insérées :",
            len(df)
        )

    else:

        print(
            "Fichier absent :",
            file
        )


print("ETL PostgreSQL terminé")
