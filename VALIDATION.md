# Bilan de vérification du laboratoire

Vérifications exécutées le 20 novembre 2026 sous Linux, Python 3.12.14. Les fichiers de dépendances verrouillées décrivent les environnements testés ; leur installation sur un autre système doit être vérifiée.

## Parcours réellement exécutés

- Installation des dépendances du laboratoire et `pip check` sans conflit.
- Validation des 344 observations du CSV réel ; normalisation des libellés de sexe.
- `python -m pytest -q` : **4 tests réussis** (contrat des données, entrée invalide, pipeline et valeurs absentes, API et journalisation).
- Entraînement et comparaison de deux candidats ; séparation stratifiée 206/69/69. Régression logistique retenue : F1 macro validation 1,00 et test 1,00 ; référence majoritaire validation environ 0,207. Ces résultats sur ce petit jeu ne démontrent aucune généralisation universelle.
- MLflow Tracking et Model Registry locaux : enregistrement de versions, contrôle qualité et promotion explicite d'un champion.
- Serveur Uvicorn réel : requête HTTP avec clé, réponse Adelie et version du modèle, enregistrement SQLite ; contrôles 401 et 422 dans les tests.
- Génération du rapport HTML Evidently et du contrôle KS, avec dérive de masse **simulée**. Aucune performance réelle en production n'est déduite de cette simulation.
- Rattachement d'un label de démonstration au journal : mécanisme vérifié, échantillon insuffisant pour évaluer la qualité du service.
- Flow Prefect local terminé : validation puis entraînement, sans promotion automatique.
- DVC dans une copie isolée : initialisation Git/DVC, ajout du CSV, stockage local, push et `dvc repro` terminés. Le suivi MLflow constitue un effet externe au cache DVC, expliqué dans le cours.
- Feast dans un environnement séparé : préparation, `feast apply`, matérialisation, récupération historique de cinq lignes et récupération en ligne.
- Lecture syntaxique des fichiers YAML et HCL. Mise en page du document Word rendue et examinée sur 40 pages.

## Configurations fournies, non exécutées ici

Docker/Compose, les tableaux Prometheus/Grafana dans les conteneurs, GitHub Actions et GHCR, le cluster kind/Kubernetes et l'application Terraform n'ont pas été exécutés dans cet environnement. Leur code est fourni pour le TP avec ses prérequis et procédures de vérification ; aucune mise en production n'est revendiquée.

Le dépôt livré ne contient ni clé, ni base MLflow préremplie, ni modèle sérialisé préchargé. Les étudiants entraînent et promeuvent leur propre version. Les fichiers `examples/` sont uniquement des résultats illustratifs de la vérification, jamais des entrées de l'API.
