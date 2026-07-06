import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier
df = pd.read_csv("data_clean/cycles_production_bloc3_propre.csv")

# ========================

print("\n========== KPI PRODUCTION ==========\n")

avg_time = df["production_time_sec"].mean()
print(f"Temps moyen de production : {avg_time:.2f} secondes")
print(f"Nombre total de cycles    : {len(df)}")
print(f"Temps minimum             : {df['production_time_sec'].min()} secondes")
print(f"Temps maximum             : {df['production_time_sec'].max()} secondes")

print("\n--- Cycles par usine ---")
for usine, nb in df["factory_id"].value_counts().sort_index().items():
    print(f"Usine {usine} : {nb} cycles")


print("\n--- Top 5 clients ---")
for client, nb in df["client_id"].value_counts().head().items():
    print(f"Client {client} : {nb} cycles")

print("\n--- Top 5 produits ---")
for produit, nb in df["product_id"].value_counts().head().items():
    print(f"Produit {produit} : {nb} cycles")

rapides = len(df[df["production_time_sec"] < 300])
lents = len(df[df["production_time_sec"] >= 300])

print("\n--- Répartition des cycles ---")
print(f"Cycles rapides (<300 s) : {rapides}")
print(f"Cycles lents (>=300 s)  : {lents}")



# =================================================================================================

production_usine = df["factory_id"].value_counts().sort_index()
top5_produits = df["product_id"].value_counts().head(5)

#1. Production par usine (barres colorées)


production_usine.plot(
    kind="bar",
    color="steelblue",
    edgecolor="black"
)

plt.title("Production par usine")
plt.xlabel("Usine")
plt.ylabel("Nombre de cycles")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

#2. Répartition des temps de production (histogramme)
plt.figure(figsize=(8,5))

plt.hist(df["production_time_sec"],
         bins=15,
         color="orange",
         edgecolor="black")

plt.title("Répartition des temps de production")
plt.xlabel("Temps (secondes)")
plt.ylabel("Nombre de cycles")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()



#3. Top 5 produits (barres horizontales)
top5_produits.plot(
    kind="barh",
    color="seagreen",
    edgecolor="black"
)

plt.title("Top 5 des produits fabriqués")
plt.xlabel("Nombre de cycles")
plt.tight_layout()

plt.show()
