# solution-big-data-indusflow
développement d'une solution big data et industrialisation pour indusflow analytics


## Objectif
Créer un pipeline ETL pour charger et transformer des données industrielles dans PostgreSQL.

## Stack
- Python
- PostgreSQL
- GitHub
- Airflow (plus tard)
- Docker (plus tard)



ssh-keygen -t ed25519 -C "ton-email-github"

Appuie sur Entrée jusqu’à la fin.

3. Ajoute la clé à GitHub

Affiche la clé :

cat ~/.ssh/id_ed25519.pub

Puis copie-colle dans :
👉 https://github.com/settings/keys
→ “New SSH key”

4. Change ton repo de HTTPS → SSH
git remote set-url origin git@github.com:amine-username/solution-big-data-indusflow.git
5. Test rapide
ssh -T git@github.com
