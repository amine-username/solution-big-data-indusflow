
"""
===========================================================================
                    KPI.PY - PILOTAGE INDUSTRIEL INDUSFLOW
===========================================================================
Script unique regroupant tous les KPI du Bloc 3 :

  - KPI Production      (cycles_production_bloc3_propre.csv)
  - KPI Qualité         (cameras_qualite_bloc3_propre.csv)
  - KPI Maintenance     (maintenance_machines_bloc3_propre.csv)
  - KPI Pannes machines (logs_erreurs_machines_bloc3_propre.csv)
  - KPI Monitoring ETL  (logs_jobs_airflow.csv)
  - KPI Capteurs        (capteurs_machines_bloc3_propre.csv)
  - KPI Alertes infra   (alertes_monitoring.csv)
  - KPI Planning        (planning_production_bloc3_propre.csv)

Tous les seuils d'alerte sont configurables en haut du fichier.
Un résumé global des alertes est affiché à la fin.
===========================================================================
"""
from sqlalchemy import create_engine
import pandas as pd
import matplotlib as plt


engine = create_engine(
    "postgresql://indusflow_user:indusflow_password@localhost:5432/indusflow"
)

# Liste qui va contenir toutes les alertes déclenchées, pour le résumé final
alertes_globales = []


def ajouter_alerte(message):
    """Enregistre une alerte pour le résumé final et l'affiche immédiatement."""
    print(f"⚠️  ALERTE : {message}")
    alertes_globales.append(message)


def ok(message):
    print(f"✅ {message}")


def titre(txt):
    print("\n" + "=" * 70)
    print(txt.center(70))
    print("=" * 70)

def charger_table(table):
    return pd.read_sql(
        f"SELECT * FROM {table}",
        engine
    )
# ==========================================================================
#                            SEUILS D'ALERTE
# ==========================================================================

# Ces seuils ont été calibrés sur la distribution réelle des données IndusFlow
# (moyenne, écart-type, quantiles observés sur chaque CSV), pour donner un
# rapport crédible : certains indicateurs passent, d'autres déclenchent une
# vraie alerte exploitable, plutôt qu'un seuil arbitraire qui fait tout sonner.

# --- Production ---
# Moyenne réelle ~305 sec (écart-type ~163). Seuil fixé au-dessus de la
# moyenne pour ne pas alerter sur un simple bruit statistique.
SEUIL_TEMPS_PRODUCTION_SEC = 400      # temps moyen max acceptable
SEUIL_TAUX_CYCLES_LENTS = 35          # % max de cycles lents toléré (réel ~32%)

# --- Qualité ---
# Taux de conformité réel ~89%, confiance caméra réelle ~0.80
SEUIL_TAUX_CONFORMITE = 85           # % min de produits conformes
SEUIL_CONFIANCE_CAMERA = 0.75        # score de confiance moyen min

# --- Maintenance ---
# Coût total réel ~400 k€, durée moyenne réelle ~195 min
SEUIL_COUT_MAINTENANCE_TOTAL = 450000  # € max sur la période
SEUIL_DUREE_MOYENNE_MIN = 220           # durée moyenne max (min)

# --- Pannes machines ---
# Volume réel ~1800 pannes loggées, taux de résolution réel ~71%,
# temps moyen de résolution réel ~360 min
SEUIL_NB_PANNES = 1600                # volume de pannes toléré sur la période
SEUIL_TAUX_RESOLUTION = 80            # % min de pannes résolues (objectif métier)
SEUIL_TEMPS_RESOLUTION_MIN = 400      # temps moyen de résolution max (min)

# --- Monitoring Airflow ---
# Taux d'échec réel ~12%
SEUIL_TAUX_ECHEC_AIRFLOW = 15         # % max de jobs en échec

# --- Capteurs ---
# Moyennes réelles : 70°C / 5.0 vibration / 10 bar (écarts-types ~10 / 1.4 / 2)
# Seuils fixés au-delà de la moyenne pour ne détecter que les vraies dérives
SEUIL_TEMPERATURE_C = 90              # °C max (~2% des relevés réels dépassent)
SEUIL_VIBRATION = 7                   # niveau max (~8% des relevés réels dépassent)
SEUIL_PRESSION_BAR = 13               # bar max (~7% des relevés réels dépassent)

# --- Alertes monitoring infra ---
# 52 alertes critiques réelles, dont 15 non résolues
SEUIL_ALERTES_CRITIQUES = 10          # nb d'alertes critiques non résolues toléré

# --- Planning ---
# Taux de retard réel ~12%
SEUIL_TAUX_RETARD = 15                # % max de plans en retard


# ==========================================================================
#                            CHARGEMENT DES DONNEES
# ==========================================================================

cycles = charger_table("cycles_production")
qualite = charger_table("cameras_qualite")
maintenance = charger_table("maintenance_machines")
pannes = charger_table("logs_erreurs_machines")
airflow = charger_table("logs_jobs_airflow")
capteurs = charger_table("capteurs_machines")
alertes_infra = charger_table("alertes_monitoring")
planning = charger_table("planning_production")
usines = charger_table("usines")


# ==========================================================================
#                            KPI PRODUCTION
# ==========================================================================

titre("KPI PRODUCTION")

if cycles is not None:

    nb_cycles = len(cycles)
    temps_moyen = cycles["production_time_sec"].mean()
    temps_median = cycles["production_time_sec"].median()
    temps_min = cycles["production_time_sec"].min()
    temps_max = cycles["production_time_sec"].max()
    ecart_type = cycles["production_time_sec"].std()

    print(f"Nombre total de cycles   : {nb_cycles}")
    print(f"Temps moyen              : {temps_moyen:.2f} sec")
    print(f"Temps médian             : {temps_median:.2f} sec")
    print(f"Temps minimum            : {temps_min} sec")
    print(f"Temps maximum            : {temps_max} sec")
    print(f"Écart-type               : {ecart_type:.2f} sec")

    # Cycles rapides / lents
    cycles_rapides = cycles[cycles["production_time_sec"] < SEUIL_TEMPS_PRODUCTION_SEC]
    cycles_lents = cycles[cycles["production_time_sec"] >= SEUIL_TEMPS_PRODUCTION_SEC]

    taux_rapides = len(cycles_rapides) / nb_cycles * 100
    taux_lents = len(cycles_lents) / nb_cycles * 100

    print(f"\nCycles rapides : {len(cycles_rapides)} ({taux_rapides:.2f}%)")
    print(f"Cycles lents   : {len(cycles_lents)} ({taux_lents:.2f}%)")

    print("\n--- Alertes production ---")
    if temps_moyen > SEUIL_TEMPS_PRODUCTION_SEC:
        ajouter_alerte("Temps moyen de production trop élevé")
    else:
        ok("Temps moyen de production conforme")

    if taux_lents > SEUIL_TAUX_CYCLES_LENTS:
        ajouter_alerte("Trop de cycles lents")
    else:
        ok("Taux de cycles lents acceptable")

    # Performance par usine
    print("\n--- Production par usine ---")
    production_usine = cycles["factory_id"].value_counts().sort_index()
    print(production_usine)

    performance_usine = cycles.groupby("factory_id")["production_time_sec"].mean()
    print("\nTemps moyen par usine :")
    print(performance_usine)

    meilleure_usine = performance_usine.idxmin()
    pire_usine = performance_usine.idxmax()
    print(f"\n🏆 Usine la plus performante : {meilleure_usine}")
    print(f"🐌 Usine la moins performante : {pire_usine}")

    # Top produits / clients
    print("\n--- Top 5 produits (par volume de cycles) ---")
    print(cycles["product_id"].value_counts().head(5))

    print("\n--- Top 5 clients (par volume de cycles) ---")
    print(cycles["client_id"].value_counts().head(5))

else:
    print("Impossible de calculer les KPI production : fichier absent")


# ==========================================================================
#                            KPI QUALITE
# ==========================================================================

titre("KPI QUALITE")

if qualite is not None:

    nb_controles = len(qualite)
    nb_defauts = qualite["defect_detected"].sum()
    taux_conformite = (1 - nb_defauts / nb_controles) * 100
    confiance_moyenne = qualite["confidence_score"].mean()

    print(f"Nombre de contrôles caméra : {nb_controles}")
    print(f"Nombre de défauts détectés : {nb_defauts}")
    print(f"Taux de conformité         : {taux_conformite:.2f}%")
    print(f"Score de confiance moyen   : {confiance_moyenne:.3f}")

    # Défauts par machine
    print("\n--- Top 5 machines avec le plus de défauts ---")
    defauts_par_machine = (
        qualite[qualite["defect_detected"] == 1]["machine_id"]
        .value_counts()
        .head(5)
    )
    print(defauts_par_machine)

    print("\n--- Alertes qualité ---")
    if taux_conformite < SEUIL_TAUX_CONFORMITE:
        ajouter_alerte("Taux de conformité qualité trop faible")
    else:
        ok("Taux de conformité qualité conforme")

    if confiance_moyenne < SEUIL_CONFIANCE_CAMERA:
        ajouter_alerte("Score de confiance caméra trop faible")
    else:
        ok("Score de confiance caméra correct")

else:
    print("Impossible de calculer les KPI qualité : fichier absent")


# ==========================================================================
#                            KPI MAINTENANCE
# ==========================================================================

titre("KPI MAINTENANCE")

if maintenance is not None:

    nb_interventions = len(maintenance)
    duree_moyenne = maintenance["duration_min"].mean()
    cout_total = maintenance["cost_eur"].sum()
    cout_moyen = maintenance["cost_eur"].mean()

    print(f"Nombre d'interventions      : {nb_interventions}")
    print(f"Durée moyenne intervention  : {duree_moyenne:.2f} min")
    print(f"Coût total maintenance      : {cout_total:,.2f} €")
    print(f"Coût moyen par intervention : {cout_moyen:,.2f} €")

    print("\n--- Répartition par type d'intervention ---")
    print(maintenance["maintenance_type"].value_counts())

    print("\n--- Répartition par statut ---")
    print(maintenance["status"].value_counts())

    print("\n--- Top 5 machines les plus maintenues ---")
    machine_plus_maintenue = maintenance["machine_id"].value_counts().head(5)
    print(machine_plus_maintenue)

    print("\n--- Alertes maintenance ---")
    if cout_total > SEUIL_COUT_MAINTENANCE_TOTAL:
        ajouter_alerte("Coût total de maintenance trop élevé")
    else:
        ok("Coût de maintenance sous contrôle")

    if duree_moyenne > SEUIL_DUREE_MOYENNE_MIN:
        ajouter_alerte("Durée moyenne des interventions trop longue")
    else:
        ok("Durée des interventions normale")

else:
    print("Impossible de calculer les KPI maintenance : fichier absent")


# ==========================================================================
#                            KPI PANNES MACHINES
# ==========================================================================

titre("KPI PANNES MACHINES")

if pannes is not None:

    nb_pannes = len(pannes)
    nb_resolues = pannes["resolved"].sum()
    taux_resolution = nb_resolues / nb_pannes * 100
    temps_resolution_moyen = pannes.loc[pannes["resolved"] == 1, "resolution_time_min"].mean()

    print(f"Nombre total de pannes       : {nb_pannes}")
    print(f"Pannes résolues              : {nb_resolues}")
    print(f"Taux de résolution           : {taux_resolution:.2f}%")
    print(f"Temps moyen de résolution    : {temps_resolution_moyen:.2f} min")

    print("\n--- Répartition par sévérité ---")
    print(pannes["severity"].value_counts())

    print("\n--- Top 5 machines les plus en panne ---")
    print(pannes["machine_id"].value_counts().head(5))

    nb_critiques = len(pannes[pannes["severity"] == "CRITICAL"])
    print(f"\nPannes critiques : {nb_critiques}")

    print("\n--- Alertes pannes ---")
    if nb_pannes > SEUIL_NB_PANNES:
        ajouter_alerte("Nombre de pannes trop élevé")
    else:
        ok("Nombre de pannes acceptable")

    if taux_resolution < SEUIL_TAUX_RESOLUTION:
        ajouter_alerte("Taux de résolution des pannes trop faible")
    else:
        ok("Taux de résolution des pannes correct")

    if temps_resolution_moyen > SEUIL_TEMPS_RESOLUTION_MIN:
        ajouter_alerte("Temps moyen de résolution des pannes trop long")
    else:
        ok("Temps de résolution des pannes correct")

else:
    print("Impossible de calculer les KPI pannes : fichier absent")


# ==========================================================================
#                            KPI MONITORING AIRFLOW
# ==========================================================================

titre("KPI MONITORING AIRFLOW")

if airflow is not None:

    nb_jobs = len(airflow)
    nb_echecs = len(airflow[airflow["status"] == "failed"])
    taux_echec = nb_echecs / nb_jobs * 100
    duree_moyenne_job = airflow["duration_sec"].mean()
    volume_total = airflow["rows_processed"].sum()

    print(f"Nombre de jobs Airflow     : {nb_jobs}")
    print(f"Jobs en échec              : {nb_echecs}")
    print(f"Taux d'échec               : {taux_echec:.2f}%")
    print(f"Durée moyenne d'un job     : {duree_moyenne_job:.2f} sec")
    print(f"Volume total de données    : {volume_total:,.0f} lignes traitées")

    print("\n--- Répartition par statut ---")
    print(airflow["status"].value_counts())

    print("\n--- Top 5 DAGs les plus exécutés ---")
    print(airflow["dag_name"].value_counts().head(5))

    print("\n--- Alertes Airflow ---")
    if taux_echec > SEUIL_TAUX_ECHEC_AIRFLOW:
        ajouter_alerte("Taux d'échec des jobs Airflow trop élevé")
    else:
        ok("Pipeline Airflow stable")

else:
    print("Impossible de calculer les KPI Airflow : fichier absent")


# ==========================================================================
#                            KPI CAPTEURS
# ==========================================================================

titre("KPI CAPTEURS MACHINES")

if capteurs is not None:

    temp_moyenne = capteurs["temperature_c"].mean()
    vib_moyenne = capteurs["vibration_level"].mean()
    pression_moyenne = capteurs["pressure_bar"].mean()

    print(f"Température moyenne : {temp_moyenne:.2f} °C")
    print(f"Vibration moyenne   : {vib_moyenne:.2f}")
    print(f"Pression moyenne    : {pression_moyenne:.2f} bar")

    nb_depassement_temp = len(capteurs[capteurs["temperature_c"] > SEUIL_TEMPERATURE_C])
    nb_depassement_vib = len(capteurs[capteurs["vibration_level"] > SEUIL_VIBRATION])
    nb_depassement_pression = len(capteurs[capteurs["pressure_bar"] > SEUIL_PRESSION_BAR])

    print(f"\nDépassements température : {nb_depassement_temp}")
    print(f"Dépassements vibration   : {nb_depassement_vib}")
    print(f"Dépassements pression    : {nb_depassement_pression}")

    print("\n--- Top 5 machines avec les plus de dépassements température ---")
    print(
        capteurs[capteurs["temperature_c"] > SEUIL_TEMPERATURE_C]["machine_id"]
        .value_counts()
        .head(5)
    )

    print("\n--- Alertes capteurs ---")
    if nb_depassement_temp > 0:
        ajouter_alerte(f"{nb_depassement_temp} dépassements de température détectés")
    else:
        ok("Aucun dépassement de température")

    if nb_depassement_vib > 0:
        ajouter_alerte(f"{nb_depassement_vib} dépassements de vibration détectés")
    else:
        ok("Aucun dépassement de vibration")

    if nb_depassement_pression > 0:
        ajouter_alerte(f"{nb_depassement_pression} dépassements de pression détectés")
    else:
        ok("Aucun dépassement de pression")

else:
    print("Impossible de calculer les KPI capteurs : fichier absent")


# ==========================================================================
#                            KPI ALERTES MONITORING INFRA
# ==========================================================================

titre("KPI ALERTES MONITORING INFRA")

if alertes_infra is not None:

    nb_alertes_infra = len(alertes_infra)
    nb_non_resolues = len(alertes_infra[alertes_infra["resolved"] == 0])
    nb_critiques_infra = len(alertes_infra[alertes_infra["severity"] == "CRITICAL"])
    nb_critiques_non_resolues = len(
        alertes_infra[
            (alertes_infra["severity"] == "CRITICAL")
            & (alertes_infra["resolved"] == 0)
        ]
    )

    print(f"Nombre total d'alertes         : {nb_alertes_infra}")
    print(f"Alertes non résolues           : {nb_non_resolues}")
    print(f"Alertes critiques              : {nb_critiques_infra}")
    print(f"Alertes critiques non résolues : {nb_critiques_non_resolues}")

    print("\n--- Répartition par système ---")
    print(alertes_infra["system_name"].value_counts())

    print("\n--- Répartition par sévérité ---")
    print(alertes_infra["severity"].value_counts())

    print("\n--- Alertes infrastructure ---")
    if nb_critiques_non_resolues > SEUIL_ALERTES_CRITIQUES:
        ajouter_alerte("Trop d'alertes critiques infrastructure non résolues")
    else:
        ok("Alertes critiques infrastructure sous contrôle")

else:
    print("Impossible de calculer les KPI alertes infra : fichier absent")


# ==========================================================================
#                            KPI PLANNING PRODUCTION
# ==========================================================================

titre("KPI PLANNING PRODUCTION")

if planning is not None:

    nb_plans = len(planning)
    nb_retard = len(planning[planning["status"] == "Delayed"])
    nb_termine = len(planning[planning["status"] == "Completed"])
    taux_retard = nb_retard / nb_plans * 100
    taux_completion = nb_termine / nb_plans * 100

    print(f"Nombre de plans de production : {nb_plans}")
    print(f"Plans en retard                : {nb_retard}")
    print(f"Plans terminés                 : {nb_termine}")
    print(f"Taux de retard                 : {taux_retard:.2f}%")
    print(f"Taux de complétion             : {taux_completion:.2f}%")

    print("\n--- Répartition par statut ---")
    print(planning["status"].value_counts())

    print("\n--- Répartition par priorité ---")
    print(planning["priority"].value_counts())

    print("\n--- Alertes planning ---")
    if taux_retard > SEUIL_TAUX_RETARD:
        ajouter_alerte("Taux de retard sur le planning de production trop élevé")
    else:
        ok("Planning de production respecté")

else:
    print("Impossible de calculer les KPI planning : fichier absent")


# ==========================================================================
#                            RESUME GLOBAL DES ALERTES
# ==========================================================================

titre("RESUME GLOBAL DES ALERTES")

if alertes_globales:
    print(f"Nombre total d'alertes déclenchées : {len(alertes_globales)}\n")
    for i, a in enumerate(alertes_globales, start=1):
        print(f"{i}. ⚠️  {a}")
else:
    print("✅ Aucune alerte déclenchée. Tous les indicateurs sont dans les clous.")


# ==========================================================================
#                            GRAPHIQUES
# ==========================================================================

print("\nGénération des graphiques...")

# --- Production par usine ---
if cycles is not None:
    plt.figure(figsize=(8, 5))
    cycles["factory_id"].value_counts().sort_index().plot(
        kind="bar", color="steelblue", edgecolor="black"
    )
    plt.title("Production par usine")
    plt.xlabel("Usine")
    plt.ylabel("Nombre de cycles")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("graph_production_par_usine.png")
    plt.show()

    # --- Répartition des temps de production ---
    plt.figure(figsize=(8, 5))
    plt.hist(cycles["production_time_sec"], bins=15, color="orange", edgecolor="black")
    plt.title("Répartition des temps de production")
    plt.xlabel("Temps (secondes)")
    plt.ylabel("Nombre de cycles")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("graph_temps_production.png")
    plt.show()

    # --- Top 5 produits ---
    plt.figure(figsize=(8, 5))
    cycles["product_id"].value_counts().head(5).plot(
        kind="barh", color="seagreen", edgecolor="black"
    )
    plt.title("Top 5 produits fabriqués")
    plt.xlabel("Nombre de cycles")
    plt.tight_layout()
    plt.savefig("graph_top5_produits.png")
    plt.show()

# --- Qualité : défauts par machine ---
if qualite is not None:
    plt.figure(figsize=(8, 5))
    qualite[qualite["defect_detected"] == 1]["machine_id"].value_counts().head(10).plot(
        kind="bar", color="crimson", edgecolor="black"
    )
    plt.title("Top 10 machines avec le plus de défauts détectés")
    plt.xlabel("Machine")
    plt.ylabel("Nombre de défauts")
    plt.tight_layout()
    plt.savefig("graph_defauts_qualite.png")
    plt.show()

# --- Maintenance : coût par type ---
if maintenance is not None:
    plt.figure(figsize=(8, 5))
    maintenance.groupby("maintenance_type")["cost_eur"].sum().plot(
        kind="bar", color="purple", edgecolor="black"
    )
    plt.title("Coût total de maintenance par type d'intervention")
    plt.xlabel("Type d'intervention")
    plt.ylabel("Coût (€)")
    plt.tight_layout()
    plt.savefig("graph_cout_maintenance.png")
    plt.show()

# --- Pannes : répartition par sévérité ---
if pannes is not None:
    plt.figure(figsize=(8, 5))
    pannes["severity"].value_counts().plot(
        kind="bar", color="darkred", edgecolor="black"
    )
    plt.title("Répartition des pannes par sévérité")
    plt.xlabel("Sévérité")
    plt.ylabel("Nombre de pannes")
    plt.tight_layout()
    plt.savefig("graph_pannes_severite.png")
    plt.show()

# --- Airflow : statut des jobs ---
if airflow is not None:
    plt.figure(figsize=(8, 5))
    airflow["status"].value_counts().plot(
        kind="bar", color="teal", edgecolor="black"
    )
    plt.title("Statut des jobs Airflow")
    plt.xlabel("Statut")
    plt.ylabel("Nombre de jobs")
    plt.tight_layout()
    plt.savefig("graph_airflow_status.png")
    plt.show()

# --- Capteurs : température moyenne par machine ---
if capteurs is not None:
    plt.figure(figsize=(10, 5))
    capteurs.groupby("machine_id")["temperature_c"].mean().sort_values(ascending=False).head(10).plot(
        kind="bar", color="tomato", edgecolor="black"
    )
    plt.axhline(SEUIL_TEMPERATURE_C, color="black", linestyle="--", label="Seuil alerte")
    plt.title("Top 10 machines les plus chaudes (température moyenne)")
    plt.xlabel("Machine")
    plt.ylabel("Température (°C)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("graph_temperature_machines.png")
    plt.show()

titre("FIN DU RAPPORT KPI")
