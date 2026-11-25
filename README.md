# EcoSpecies MLOps
Cours de 5e année ingénieur. Lire COURS_COMPLET.md ou le document Word fourni. Données réelles Palmer Penguins incluses ; dérive simulée séparément.

## Démarrage rapide
Depuis ce dossier, Python 3.12 :
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m eco.validate
python -m pytest -q
python -m eco.train
```
Lire reports/candidate.json et remplacer N par la version enregistrée :
```bash
python -m eco.promote --version N
export API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m uvicorn eco.api:app --host 127.0.0.1 --port 8000
```
API http://127.0.0.1:8000/docs . Avec Poetry : poetry install puis poetry run avant les commandes Python. Aucun identifiant fixe n'est fourni. La même clé doit être connue des clients. Ne pas publier les secrets.

## Interfaces
- API /docs, /health, /ready, /metrics sur 8000.
- MLflow : `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001` depuis ce dossier.
- Prefect : `python -m eco.flow` ; serveur persistant facultatif sur 4200.
- Dérive : `python -m eco.monitor` produit reports/drift.html.
- Docker : définir API_KEY et GRAFANA_PASSWORD puis `docker compose up --build -d` ; Prometheus 9090, Grafana 3000 (login admin, votre mot de passe).

## Organisation
- eco/ : validation, entraînement, promotion, API, monitoring, orchestration.
- data/ : CSV et source ; tests/ : tests automatisés.
- monitoring/ : configurations Prometheus et Grafana.
- .github/workflows/ : CI et CD contrôlé.
- infra/ : kind et Terraform pour le parcours avancé.
- feast_repo/ : feature store local dans un environnement séparé.
- scripts/smoke.py : prédiction réelle HTTP ; API_KEY requise.
- dvc.yaml : dépendances du pipeline ; initialiser Git et DVC selon le cours.

## Précautions de méthode
Le test n'est pas une cible d'optimisation. Petit dataset et découpage aléatoire : pas de preuve de généralisation universelle. La promotion est explicite. La dérive n'est pas une mesure de performance sans labels. Joblib et cloudpickle : artefacts locaux de confiance uniquement. Kubernetes fournit un laboratoire avec un réplica et journaux éphémères ; pas une architecture de production durable.

## Nettoyage
Ctrl+C pour les processus Python ; docker compose down conserve les volumes. Pour le laboratoire avancé, examiner puis exécuter terraform -chdir=infra destroy et kind delete cluster --name ecospecies. Ne pas supprimer un stockage partagé ou un état inconnu.

## Validation
Voir VALIDATION.md pour les commandes réellement exécutées et leurs limites. Les fichiers requirements-lock.txt et feast_repo/requirements-lock.txt figent les environnements Python testés. Docker, Terraform et les workflows doivent être vérifiés sur le poste d'exécution selon les prérequis du cours.
