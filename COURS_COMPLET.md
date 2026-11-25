# Cours de MLOps de bout en bout

EcoSpecies
Développement et déploiement d’applications intelligentes
Niveau cinquième année ingénieur

Ce cours conduit du besoin métier à un service de classification surveillé. Il utilise des données réelles Palmer Penguins et une stack locale. L’étudiant doit pouvoir identifier les versions du code, des données et du modèle, expliquer les tests, livrer une API et revenir à une version précédente.

Le tableau fourni contient des alternatives. Le parcours implémente Python, Pandas, scikit-learn, bash, venv ou Poetry, Git et GitHub, pytest et Pandera, MLflow Tracking et Registry, DVC, FastAPI, Docker Compose, GitHub Actions, Evidently, Prometheus, Grafana et Prefect. Le complément avancé utilise Kubernetes, Terraform et Feast. GitLab, Jenkins, Flask, Django, Airflow et Kubeflow sont comparés, pas dupliqués.

Organisation proposée : huit séances de trois heures pour le socle et trois séances supplémentaires pour l’infrastructure et Feast. Adapter cette durée au niveau réel du groupe. Aucun abonnement cloud ni clé de LLM n’est nécessaire pour le socle.

Prérequis : fonctions Python, DataFrame, Git de base, HTTP, notions d’apprentissage supervisé. Poste conseillé : Python 3.12, 8 Go de RAM pour le socle ; environ 16 Go pour le laboratoire Kubernetes local. Ce sont des repères pratiques, pas des minimums garantis.

La preuve d’exécution et ses limites sont dans VALIDATION.md. Les configurations Docker, GitHub et Kubernetes ne sont déclarées testées que si elles ont réellement été exécutées. Le dépôt fourni est un laboratoire local, pas une plateforme publique sécurisée prête à commercialiser.




# 1 DevOps et MLOps

DevOps est un ensemble de pratiques de collaboration et d’automatisation entre développement et exploitation. MLOps applique ces principes aux systèmes ML, en ajoutant le cycle de vie des données, des expériences et des modèles.

Un logiciel peut continuer à répondre correctement au protocole HTTP alors que ses prédictions se dégradent. La qualité opérationnelle et la qualité statistique sont donc deux dimensions distinctes.

| Dimension | DevOps | MLOps |
| Livrable | Code et application | Code, données, prétraitement, modèle |
| Validation | Tests logiciels | Tests logiciels et données et évaluation ML |
| Version | Commit, dépendances, image | Les mêmes et dataset, run, modèle |
| Surveillance | Disponibilité, erreurs, latence | Les mêmes et distributions et qualité |
| Évolution | Changement du logiciel | Également nouvelles données ou concept |

CI : intégration continue, vérifications automatiques à chaque modification. CD : livraison continue, puis éventuellement déploiement continu selon les règles d’approbation. CT : entraînement continu, déclenché de manière contrôlée par une planification, de nouvelles données ou une décision.

Un entraînement terminé ne justifie pas une promotion. La qualité doit être mesurée et la politique d’acceptation appliquée. Une alerte de dérive déclenche une investigation, pas une garantie qu’un réentraînement résoudra le problème.

Question de cours : donner un cas où l’API est disponible mais le modèle inadéquat. Réponse attendue : le régime des observations change sans erreur technique du service.




# 2 Sujet et dictionnaire des données

EcoSpecies identifie Adelie, Chinstrap ou Gentoo à partir de mesures de manchots. C’est une classification supervisée multiclasse et du ML classique. Aucun LLM, GPU ou accès à une API générative n’est requis.

| Colonne | Rôle | Unité ou valeurs |
| bill_length_mm | Caractéristique | Longueur du bec en mm |
| bill_depth_mm | Caractéristique | Profondeur du bec en mm |
| flipper_length_mm | Caractéristique | Longueur de nageoire en mm |
| body_mass_g | Caractéristique | Masse en grammes |
| island | Caractéristique | Biscoe, Dream, Torgersen |
| sex | Caractéristique | Male, Female ou absent |
| species | Cible | Adelie, Chinstrap, Gentoo |

Le CSV inclus contient 344 observations. Le prétraitement harmonise la casse du sexe. Deux observations ont des mesures physiques manquantes et onze n’ont pas de sexe renseigné. Les valeurs manquantes sont imputées dans le pipeline appris, sans supprimer toute la ligne.

Source : copie CSV publique Seaborn du dataset Palmer Penguins. Auteurs du package : Allison Horst, Alison Hill et Kristen Gorman ; observations liées aux travaux de Gorman et collaborateurs. Licence et références détaillées : data/SOURCE.md. Le dataset original peut avoir davantage de colonnes ; ce TP utilise la copie à sept colonnes.

Limites : petit dataset, sites et périodes limités. island peut être très informatif et ne pas généraliser à une autre zone géographique. Un score élevé sur une séparation aléatoire ne prouve pas la qualité sur une nouvelle campagne. Les horodatages du TP Feast sont artificiels ; le décalage de masse du rapport de dérive est simulé.




# 3 Architecture et correspondance des outils

Le pipeline d’entraînement lit le CSV, valide son schéma, découpe les données, ajuste le prétraitement et compare deux modèles. MLflow conserve les expériences et enregistre une version candidate. La promotion explicite exporte un bundle figé qui est inclus dans l’image Docker de l’API.

Le client envoie du JSON à FastAPI. L’API valide, prédit et écrit dans SQLite : identifiant de requête, date, version du modèle, caractéristiques et espèce prédite. Prometheus collecte les métriques ; Grafana les présente. Evidently et les contrôles statistiques comparent un lot courant au lot de référence.

Trois registres ne doivent pas être confondus : Git garde les fichiers de code ; DVC référence les fichiers de données avec leur stockage ; MLflow organise les expériences et modèles. Le registre OCI GHCR stocke les images de l’application.

| Besoin | Outil implémenté | Fichier principal |
| Traitement et ML | Pandas et scikit-learn | eco/data.py, eco/train.py |
| Contrat de données | Pandera | eco/data.py |
| Tests | pytest | tests/test_system.py |
| Expériences et versions | MLflow | eco/train.py, eco/promote.py |
| Données et pipeline | DVC | dvc.yaml |
| API | FastAPI | eco/api.py |
| Conteneurs et observabilité | Compose, Prometheus, Grafana | compose.yaml, monitoring/ |
| CI et CD | GitHub Actions | .github/workflows/ |
| Orchestration | Prefect | eco/flow.py |
| Infrastructure | kind, Kubernetes, Terraform | infra/ |
| Feature store | Feast | feast_repo/ |

Le cours ne nécessite pas toutes les infrastructures simultanément. Le socle Python fonctionne d’abord seul ; les outils sont ajoutés progressivement.




# 4 Terminal et environnements

Un environnement virtuel isole les bibliothèques Python. Le terminal lance les programmes ; bash ou zsh interprète les commandes. Un chemin relatif dépend du dossier courant. Toutes les commandes suivantes partent du dossier EcoSpecies_MLOps, contenant config.json.

Méthode recommandée pour reproduire la validation :
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip check
```
Sous Windows, remplacer l’activation par .venv\Scripts\activate ; les scripts bash nécessitent WSL ou Git Bash. Le fichier lock pip décrit l’environnement Linux Python 3.12 testé. Pour une plateforme qui ne peut pas le résoudre, utiliser requirements.txt puis noter les versions et refaire les tests.

Alternative Poetry :
```bash
poetry env use python3.12
poetry install
poetry run python -m pytest -q
```
Ne pas superposer une installation pip globale, un environnement conda et un environnement Poetry. Dans la suite, python suppose l’environnement venv activé ; avec Poetry, préfixer chaque commande Python par poetry run.

requirements.txt indique des intervalles compatibles ; requirements-lock.txt fige les versions résolues. La bibliothèque scikit-learn du service doit correspondre à celle qui a produit le modèle. requirements-runtime.txt fige les dépendances directes critiques de l’image. Pour une production strictement reproductible, verrouiller également tout le graphe runtime et le digest de l’image de base.

Critère de réussite : python -m pip check ne signale aucun conflit et les imports nécessaires fonctionnent.




# 5 Git et collaboration

Git conserve l’histoire des fichiers texte. Un commit est un état nommé par un identifiant. Une branche isole une évolution. Une pull request permet la revue et déclenche les vérifications. GitHub ou GitLab hébergent les dépôts et la collaboration.

Commencer localement :
```bash
git init
git branch -M main
git status
```
Configurer votre nom et votre adresse avec git config si nécessaire. Initialiser DVC avant le premier git add global, comme au chapitre suivant, pour ne pas suivre directement le CSV volumineux à la fois avec Git et DVC.

Après l’initialisation DVC :
```bash
git add .
git commit -m "Initialiser le laboratoire EcoSpecies"
```
Créer un dépôt distant vide puis ajouter son URL réelle avec git remote add origin URL et pousser avec git push -u origin main. Ne pas réajouter origin s’il existe déjà. Aucune création ou publication distante n’est exécutée automatiquement par le support de cours.

.gitignore exclut les environnements, bases locales, secrets et états Terraform. Ne pas y mettre le code du projet ni tous les CSV par défaut : les fichiers réellement versionnés par DVC seront exclus individuellement par DVC.

Bonne pratique : une branche par travail, tests avant fusion et revue des changements de données, métriques et seuils. Changer un seuil pour faire passer un mauvais modèle doit être justifié dans la revue.




# 6 DVC et versions des données

DVC conserve des métadonnées et des empreintes de fichiers dans Git ; les octets sont dans un cache et éventuellement un stockage distant. Git seul est adapté au code ; DVC permet de retrouver un dataset associé à un commit sans placer tous ses octets dans Git.

Depuis le dossier du projet, avant git add :
```bash
dvc init
dvc add data/penguins.csv
mkdir -p "$HOME/ecospecies-dvc-store"
dvc remote add -d classroom "$HOME/ecospecies-dvc-store"
dvc push
git add .dvc .dvcignore data/penguins.csv.dvc data/.gitignore
git commit -m "Versionner le dataset avec DVC"
```
Le remote local évite des frais et apprend les commandes ; ce n’est pas un stockage partagé entre machines. Pour un groupe, le remplacer par un stockage accessible à tous, avec des accès adaptés. Un registre MLflow ne remplace pas ce stockage.

Pour récupérer le dataset correspondant à un état Git déjà choisi :
```bash
dvc pull
```
Pour exécuter le pipeline déclaré :
```bash
dvc repro
```
Les stages validate et train sont dans dvc.yaml. DVC examine leurs dépendances et peut réutiliser son cache. Il ne rejoue pas nécessairement les effets externes : restaurer un rapport depuis le cache ne recrée pas une version dans un autre registre MLflow. Pour enregistrer une nouvelle expérience explicitement : python -m eco.train ou dvc repro --force.

Conserver dvc.lock après exécution. Ne pas supprimer le dataset courant avec dvc checkout sans comprendre quelle version est référencée. Exercice : modifier une mesure valide, observer le changement d’empreinte, puis restaurer l’état choisi.




# 7 Qualité des données et Pandera

Un contrat de données définit les colonnes, types, valeurs acceptées et règles de qualité. Il détecte une rupture d’unité, de catégorie ou de structure avant l’entraînement. Pandera exprime ce contrat pour un DataFrame ; il ne prouve pas la représentativité statistique.

Le fichier eco/data.py vérifie exactement sept colonnes, les espèces, les îles, les intervalles numériques et le taux de valeurs absentes. Les bornes du TP sont des contrôles de plausibilité proposés, pas des lois biologiques universelles. La taille minimale et les effectifs des classes sont aussi vérifiés.

```python
pa.Column(float,
          checks=pa.Check.in_range(20, 80),
          nullable=True, coerce=True)
```
float impose le type numérique ; in_range vérifie les limites ; nullable autorise une absence ; coerce demande une conversion compatible. strict=True refuse une colonne inattendue, notamment une cible accidentellement ajoutée aux entrées.

```bash
python -m eco.validate
```
Résultat : reports/data_validation.json contient effectifs, absences et SHA256 du CSV. L’empreinte identifie le contenu, pas sa qualité.

Exercice : dans une copie du CSV, remplacer une masse en grammes par une masse en kilogrammes. La valeur doit être refusée. Ne pas modifier directement le dataset de référence pour tous les exercices. Une erreur de schéma doit arrêter les étapes dépendantes, pas être silencieusement ignorée.




# 8 Prétraitement et fuites de données

Une caractéristique est une information disponible au moment de la prédiction. La cible est la réponse connue pendant l’apprentissage. Une fuite apparaît lorsque le processus utilise une information qu’il n’aurait pas en conditions réelles ou lorsqu’il apprend le prétraitement sur l’ensemble de test.

Le TP crée une séparation stratifiée : 206 observations train, 69 validation, 69 test. La stratification préserve approximativement la proportion des espèces. La graine fixe rend le découpage reproductible. La validation choisit le modèle ; le test n’est consulté qu’après ce choix dans une exécution.

Le ColumnTransformer traite les colonnes numériques et catégorielles séparément. Numériques : imputation médiane et StandardScaler. Catégorielles : imputation par modalité fréquente et OneHotEncoder. Le Pipeline associe ce prétraitement au classifieur.

```python
model = Pipeline([
    ("prep", preprocessor()),
    ("classifier", classifier)
])
model.fit(X_train, y_train)
```
fit apprend les médianes, modalités, transformations et paramètres du classifieur sur le train. predict applique ces transformations apprises aux nouvelles entrées sans les réajuster. normalize transforme les null JSON en NaN, pour conserver la même convention au service.

Limites méthodologiques : ne pas comparer de nombreux candidats en utilisant sans cesse le même test pour décider. Pour un projet réel, réserver un test temporel ou par groupe pertinent, et organiser la validation croisée. Si plusieurs mesures proviennent d’un même individu, séparer les groupes plutôt que les lignes au hasard.




# 9 Modèles et métriques

Deux candidats sont comparés : LogisticRegression et RandomForestClassifier. La régression logistique, malgré son nom, est utilisée ici pour classer. La forêt agrège des arbres de décision. Le DummyClassifier prédit toujours la classe majoritaire et fournit une référence simple.

Accuracy = nombre de prédictions correctes divisé par nombre d’observations. Pour une classe, précision = vrais positifs / prédictions positives ; rappel = vrais positifs / positifs réels. F1 = 2 × précision × rappel / (précision + rappel). Le F1 macro est la moyenne des F1 des classes et accorde le même poids à chacune.

Les seuils proposés sont dans config.json : F1 validation au moins 0,85, supérieur au Dummy, puis F1 test au moins 0,85. Ces valeurs sont des critères pédagogiques à justifier ; elles ne garantissent pas une qualité métier suffisante. Un modèle peut avoir un bon score global mais échouer sur un sous-groupe.

```bash
python -m eco.train
```
Chaque candidat est suivi dans MLflow. Le meilleur sur validation est enregistré dans le registre avec un tag quality_gate. reports/candidate.json contient version, run_id, empreinte, scores et rapport par classe. Si les critères échouent, le script signale une erreur ; aucun champion n’est remplacé.

Résultat observé dans la validation de ce livrable : candidat logistique, F1 validation 1,00 et F1 test 1,00 ; le Dummy est proche de 0,207 sur validation. Un résultat parfait sur 69 observations faciles reste limité : pas une preuve de robustesse biologique générale.




# 10 MLflow Tracking

Une expérience est une collection de runs. Un run est une exécution avec paramètres, métriques, tags et artefacts. Les paramètres décrivent les choix, les métriques évaluent les sorties, les tags ajoutent la provenance ; les artefacts sont des fichiers produits.

MLflow Tracking permet de comparer sans se fier aux noms de fichiers comme model_final_v3. Le TP utilise une base SQLite locale mlflow.db ; MLflow conserve aussi des artefacts sur disque. Ne partager ni supprimer l’un sans comprendre ses références à l’autre.

```python
with mlflow.start_run(run_name=name):
    mlflow.log_params({"algorithm": name, "seed": 42})
    mlflow.log_metrics({"validation_f1_macro": score})
```
Ouvrir l’interface, depuis le même dossier et avec la même base :
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
```
URL : http://127.0.0.1:5001. Le port 5001 évite les conflits courants avec certains services macOS. L’API de prédiction reste sur 8000.

La signature enregistrée décrit les entrées et sorties du modèle. Le code choisit explicitement cloudpickle pour ce laboratoire local et ne charge que ses propres artefacts ; ces formats peuvent exécuter du code lors du chargement. Une plateforme réelle exige une chaîne de confiance et une maîtrise des accès aux artefacts.

Exercice : comparer les deux runs, relever l’algorithme, le seed, le F1 de validation, les empreintes et l’identifiant de run. Expliquer pourquoi deux fichiers identiques de code peuvent produire des modèles différents si les données changent.




# 11 Registre promotion et retour arrière

MLflow Model Registry conserve des versions d’un modèle nommé. Un alias est une référence modifiable vers une version. Le TP utilise champion et previous. La version d’API v1, la version du registre et le tag de l’image Docker ne désignent pas la même chose.

Lire reports/candidate.json, puis remplacer N par sa version :
```bash
python -m eco.promote --version N
```
La commande refuse une version sans tag qualité passed. Elle charge le modèle enregistré, exporte artifacts/champion.joblib avec version et run_id, puis change l’alias. L’ancien champion est conservé comme previous. L’export est atomique au niveau du fichier local ; la modification du registre et le déploiement ne constituent pas une transaction distribuée.

L’API charge un bundle figé au démarrage. Modifier un alias ne change donc pas magiquement le processus déjà lancé. Redémarrer l’API ou reconstruire l’image et la redéployer. Cela rend la version en service identifiable.

Retour arrière local : promouvoir explicitement une ancienne version acceptée, puis redémarrer. Sur Kubernetes : kubectl rollout undo revient à l’image précédente ; vérifier ensuite /ready et une prédiction. Ne jamais revenir seulement au classifieur en laissant un prétraitement incompatible.

Les deux promotions de versions 1 puis 2 de la validation ont produit les mêmes résultats, car les données et paramètres n’ont pas changé. Dans le TP, simuler une version candidate refusée en augmentant un seuil au-dessus du score possible, et constater que le champion reste inchangé.




# 12 FastAPI et service de prédiction

Une API fournit un contrat HTTP. FastAPI utilise Pydantic pour vérifier le JSON et génère OpenAPI, accessible dans /docs. Le serveur Uvicorn exécute l’application. Une dépendance vérifie X-API-Key ; ce mécanisme de TP ne remplace pas une gestion d’utilisateurs et de rôles.

```bash
export API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m uvicorn eco.api:app --host 127.0.0.1 --port 8000
```
Ne pas fermer ce terminal. Conserver la même clé pour le client. Aucune clé de démonstration fixe n’est distribuée. Les fichiers de secrets ne vont pas dans Git. Une variable exportée dans un terminal n’existe pas automatiquement dans un autre : exporter la valeur conservée ou lancer le client depuis le même environnement de shell.

| Route | Usage |
| GET /health | Vérifier que le processus répond |
| GET /ready | Vérifier la disponibilité du modèle et sa version |
| POST /api/v1/predict | Prédire avec X-API-Key |
| GET /metrics | Métriques techniques pour Prometheus |
| GET /docs | Documentation interactive |

Les champs numériques sont bornés, les catégories connues, les infinis refusés et les champs inattendus interdits. Au moins une mesure physique est requise. Une prédiction renvoie request_id, species et model_version. SQLite conserve les entrées pour l’analyse ultérieure. La réponse 200 est un succès ; 401 signale un défaut de clé ; 422 un JSON non conforme.

Limites du TP : métriques accessibles sur le réseau local, SQLite et clé partagée. Avant production : HTTPS, authentification appropriée, contrôle d’accès, limitation de débit, collecte de journaux et chaîne d’artefacts de confiance.




# 13 Appels et tests avec pytest

Le test du schéma vérifie une source valide et le refus d’une masse négative. Le test de Pipeline vérifie une prédiction avec une catégorie manquante. Le test API utilise une base temporaire et un modèle de test indépendant du champion.

```bash
python -m pytest -q
python scripts/smoke.py
```
Le second appel nécessite une API démarrée et API_KEY dans son environnement. Le script utilise requests et un timeout. Il vérifie le code HTTP puis affiche le JSON. Un test HTTP ne valide pas à lui seul l’exactitude statistique.

Pour tester à la main dans un shell qui connaît la clé :
```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750,"island":"Torgersen","sex":"Male"}'
```
Dans Postman, créer le même POST, choisir Body puis raw JSON et ajouter X-API-Key. Enregistrer seulement la structure de la requête, sans partager la vraie clé.

Exercice : tester absence de clé, masse négative, catégorie inconnue, mesure absente et demande valide. Contrôler que seule la demande valide est journalisée. Tester un redémarrage avec un autre champion et vérifier model_version. Les tests sont nécessaires avant et après la construction de l’image.




# 14 Docker et Docker Compose

Une image est un modèle d’environnement exécutable ; un conteneur est une instance de cette image. Le Dockerfile installe les dépendances runtime, copie le code et le champion, puis lance Uvicorn avec un utilisateur non root. Le modèle doit être promu avant la construction.

```bash
docker build -t ecospecies:classroom .
export GRAFANA_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker compose up --build -d
```
Compose crée API, Prometheus et Grafana dans un réseau commun. Prometheus atteint api:8000 ; Grafana atteint prometheus:9090. Ces noms internes ne sont pas des adresses à saisir dans le navigateur.

| Interface | Adresse locale |
| FastAPI et documentation | http://127.0.0.1:8000/docs |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |

Grafana utilise le login admin et le mot de passe défini dans GRAFANA_PASSWORD. Les volumes conservent le journal API et les données des outils. docker compose down arrête sans effacer ces volumes ; ne pas ajouter -v si l’on veut les garder.

Les ports sont liés à 127.0.0.1. Il ne s’agit pas d’une exposition publique. Le mot de passe Grafana ne se réinitialise pas automatiquement à chaque changement de variable si son volume existe déjà. Pour une mise à jour du modèle, reconstruire et relancer le service API.

Les images d’outils sont fixées à des tags d’exemple ; avant exposition réelle, contrôler leurs correctifs, les digests, les accès et les sauvegardes. Docker ne garantit ni sécurité automatique ni reproductibilité statistique à lui seul.




# 15 CI CD avec GitHub Actions

Un workflow décrit les événements et les jobs. Un runner exécute les commandes. ci.yml s’exécute sur push, pull_request ou demande manuelle. Il installe l’environnement verrouillé, valide, teste, entraîne et promeut uniquement dans son registre CI isolé, puis construit l’image.

Une exécution automatique ne publie rien. Une exécution manuelle publie l’image dans GHCR avec le commit SHA comme tag, après les contrôles. GITHUB_TOKEN est fourni par GitHub et limité par permissions. La publication réelle nécessite un dépôt GitHub et les droits correspondants ; elle n’est pas effectuée ici.

CD est séparé dans deploy.yml : un déclenchement manuel choisit une image, puis un runner self-hosted doté de kubectl met à jour un cluster déjà créé. Configurer l’environnement classroom avec les protections disponibles dans votre compte ; ne pas supposer qu’une simple déclaration environment active une approbation.

Le runner qui déploie doit être dédié à un dépôt de confiance, jamais à l’exécution libre de code de pull requests externes. Le cluster doit pouvoir lire l’image : la rendre accessible ou configurer imagePullSecrets. Fournir une image avec un digest ou un tag SHA vérifié, et non latest.

Point de gouvernance : Terraform crée les ressources initiales, tandis que le workflow change ensuite l’image. Cela crée une différence avec l’état Terraform. Mettre aussi à jour la variable image dans le prochain plan Terraform ; ne pas laisser deux outils réconcilier des valeurs contradictoires.

GitLab CI et Jenkins réalisent les mêmes grandes fonctions avec d’autres formats et modes d’administration. Azure Pipelines est une autre alternative. L’objectif du cours est de comprendre le déclencheur, les tests, les artefacts, les secrets et les décisions de livraison.




# 16 Dérive des données et Evidently

La dérive des données est un changement de distribution des entrées. La dérive du concept est un changement de relation entre entrées et cible. La baisse de performance est une augmentation de l’erreur ou une diminution d’une métrique ; elle ne se déduit pas automatiquement d’une dérive d’entrée.

Le rapport par défaut copie 150 observations puis ajoute 1 200 grammes à la masse. Il s’agit explicitement d’un scénario synthétique, pas d’une évolution observée du vivant.

```bash
python -m eco.monitor
# Autre lot contenant les mêmes colonnes numériques
python -m eco.monitor --current data/current.csv
```
reports/drift.html est le rapport Evidently. reports/drift.json contient un contrôle complémentaire KS sur les quatre colonnes numériques. On exige au moins 50 observations de chaque côté. Pour ce TP, la p-value est comparée à 0,01/4 pour limiter les comparaisons multiples.

Une p-value n’est pas une mesure de gravité métier ; elle dépend notamment de l’effectif. Examiner aussi les distributions, l’ampleur du changement, le mécanisme de collecte, les unités et les sous-groupes. L’imputation et l’exclusion des absences dans ce rapport peuvent masquer des problèmes : surveiller séparément le taux d’absences.

La dérive simulée ne déclenche aucun remplacement automatique. Décision attendue : vérifier une erreur d’unité ou de capteur, puis envisager de nouvelles données annotées, une évaluation et éventuellement un modèle candidat.




# 17 Qualité réelle et labels retardés

Sans réponse correcte, on peut surveiller la disponibilité et les entrées mais pas calculer honnêtement l’exactitude. Une prédiction n’est pas un label. Dans ce TP, un expert peut confirmer l’espèce après la demande ; un request_id permet de joindre cette réponse au journal.

Préparer un fichier CSV avec exactement une ligne par réponse disponible :
```text
request_id,species
IDENTIFIANT_RETOURNE_PAR_API,Adelie
```
Puis :
```bash
python -m eco.evaluate_logs --labels data/labels.csv
```
Le script refuse les doublons, valide les espèces, joint les identifiants et calcule le F1 par version de modèle. Le rapport inclut la couverture des labels. Une couverture faible ou sélective peut biaiser l’évaluation : les seules demandes revues ne représentent pas forcément tous les appels.

Ne pas utiliser des labels inventés pour annoncer une qualité en production. Dans les exercices, une étiquette connue du CSV permet un contrôle de bout en bout, mais cette démonstration n’est pas une évaluation indépendante de la production.

Le code ne déclenche aucun réentraînement sur ce fichier. Une décision de CT doit contrôler provenance, qualité, représentativité et risque de fuite. Le modèle précédemment en service constitue une référence à comparer, avec un jeu d’évaluation adapté.




# 18 Prometheus et Grafana

Prometheus collecte périodiquement des séries temporelles. Un Counter compte des événements cumulés ; un Histogram observe des durées et leurs classes. Grafana interroge la source Prometheus pour construire des tableaux de bord.

Le TP expose eco_predictions_total, eco_prediction_seconds et eco_errors_total. La variable up vient de Prometheus et indique le succès de collecte ; elle ne remplace pas un test métier complet. L’histogramme mesure la section de prédiction, pas tout le trajet réseau.

Exemples de PromQL :
```text
rate(eco_predictions_total[5m])
sum by(status)(rate(eco_errors_total[5m]))
histogram_quantile(0.95,
  sum by(le)(rate(eco_prediction_seconds_bucket[5m])))
```
rate transforme un compteur en débit ; le p95 estime une durée sous laquelle se situent environ 95 % des observations. Générer plusieurs requêtes puis attendre quelques collectes avant d’interpréter les courbes ; une absence de données n’est pas forcément un zéro.

Les fichiers de provisioning créent la source et le dashboard EcoSpecies sans saisie manuelle. Les identifiants de requête ne sont pas des labels Prometheus : ils créeraient une cardinalité non bornée. Les erreurs sont groupées par code HTTP.

Le TP fournit des graphiques mais pas de routage d’alertes vers un téléphone ou une messagerie. En prolongement, définir des règles, un délai de confirmation et un responsable de traitement. Distinguer alerte technique, statistique et métier.




# 19 Orchestration avec Prefect

Un orchestrateur exécute des tâches dans un ordre, conserve leur état et gère reprises, planification et visibilité. Un Pipeline scikit-learn organise les transformations d’un modèle ; un flow Prefect organise les étapes opérationnelles. Ces deux niveaux ne sont pas interchangeables.

```python
@task(retries=1, retry_delay_seconds=2)
def validate_task():
    return validate()

@flow(name="ecospecies-training")
def pipeline():
    validate_task()
    return train_task()
```
Exécuter immédiatement :
```bash
python -m eco.flow
```
Le processus peut démarrer un serveur temporaire Prefect. Pour une interface persistante, lancer prefect server start dans un autre terminal puis définir PREFECT_API_URL=http://127.0.0.1:4200/api. Le port 4200 sert l’interface Prefect.

La validation possède un retry ; l’entraînement n’en a pas pour éviter de créer des versions en double après une erreur ambiguë. L’idempotence signifie qu’une répétition ne crée pas d’effets indésirables. Les opérations de stockage et de promotion exigent une attention particulière.

Une planification peut être ajoutée à un déploiement Prefect après configuration ; le TP ne crée pas de tâche périodique distante et ne réentraîne pas quotidiennement sans décision. Airflow est adapté aux DAG de traitements ; Kubeflow Pipelines cible des workflows ML sur Kubernetes. Prefect est choisi ici pour une exécution locale progressive.




# 20 Kubernetes et Terraform

Kubernetes maintient un état souhaité pour des conteneurs. Un Pod héberge l’application ; un Deployment gère les réplicas et mises à jour ; un Service fournit une adresse réseau stable ; un Secret transporte une configuration sensible. Un Secret Kubernetes n’est pas une garantie de chiffrement ou de contrôle d’accès suffisant.

kind crée un cluster Kubernetes local en conteneurs. Il faut Docker et les outils kind, kubectl et Terraform installés sur le poste. Terraform décrit des ressources, calcule un plan puis applique les changements ; son état garde leurs identifiants et peut contenir des secrets.

```bash
kind create cluster --config infra/kind.yaml
docker build -t ecospecies:classroom .
kind load docker-image ecospecies:classroom --name ecospecies
export TF_VAR_api_key="$API_KEY"
terraform -chdir=infra init
terraform -chdir=infra plan
terraform -chdir=infra apply
kubectl -n ecospecies port-forward service/ecospecies 8000:8000
```
Arrêter préalablement l’API locale ou Compose pour libérer le port 8000. Lire et approuver le plan Terraform à l’invite. Le code crée un namespace, un secret, un Deployment et un Service, pas un cluster cloud payant.

Liveness détecte une application non fonctionnelle ; readiness contrôle si elle peut recevoir du trafic. Les limites CPU/mémoire évitent une consommation non maîtrisée. Le TP utilise un seul réplica et des journaux SQLite locaux au Pod, donc non durables après remplacement. Pour plusieurs réplicas, externaliser les journaux et le stockage.

Nettoyage après examen : terraform -chdir=infra destroy, puis kind delete cluster --name ecospecies. L’état et les fichiers de plan ne vont pas dans Git. Les commandes sont fournies pour le laboratoire ; leur exécution réelle dépend des outils disponibles.




# 21 Feature store avec Feast

Une feature store organise la définition et l’accès aux caractéristiques ML. Le magasin offline sert l’apprentissage historique ; le magasin online fournit rapidement les valeurs disponibles pour une entité. La matérialisation copie les valeurs vers l’online store. Une jointure point-in-time évite d’utiliser une valeur qui n’était pas encore disponible à la date étudiée.

Le complément Feast est isolé dans un autre venv pour réduire les conflits de dépendances. L’entité observation utilise observation_id. La FeatureView measurements décrit les six caractéristiques, et FeatureService penguin_features les regroupe. La cible species est exclue.

Depuis le dossier du projet :
```bash
python3.12 -m venv .venv-feast
.venv-feast/bin/python -m pip install -r feast_repo/requirements-lock.txt
cd feast_repo
../.venv-feast/bin/python prepare.py
../.venv-feast/bin/feast apply
../.venv-feast/bin/feast materialize-incremental "$(date -u +%Y-%m-%dT%H:%M:%S)"
../.venv-feast/bin/python client.py
```
prepare.py crée du Parquet et des dates fictives de disponibilité pour enseigner le mécanisme. client.py effectue une récupération historique et une récupération online de l’observation 0. Si API_KEY est définie et l’API lancée, il transmet ces caractéristiques au même endpoint et affiche sa réponse.

Le modèle de base a été entraîné depuis le CSV normalisé ; ce complément vérifie les mêmes noms et conventions. Pour une plateforme réelle, construire aussi le dataset d’entraînement à partir de la feature store et contrôler la cohérence offline/online. Feast n’est ni un moteur de prédiction ni un remplacement du registre MLflow.




# 22 Parcours de TP et évaluation

| Séance | Objectif | Preuve à remettre |
| 1 | DevOps, MLOps, environnement, données | Dictionnaire et environnement |
| 2 | Git, DVC et Pandera | Commit, empreinte et rejet de donnée invalide |
| 3 | Pipeline et métriques | Découpage justifié et comparaison Dummy |
| 4 | Tracking et Registry | Deux runs, candidat et champion |
| 5 | API et tests | JSON valide et refus 401/422 |
| 6 | Docker et CI | Image construite et tests CI |
| 7 | Dérive et observabilité | Rapport et dashboard commentés |
| 8 | Orchestration et incident | Flow et retour arrière documentés |
| Avancé | Kubernetes, Terraform et Feast | Plan et récupération online/offline |

Barème proposé sur 20 : données et reproductibilité 4 ; évaluation et traçabilité 4 ; API et tests 3 ; déploiement et CI/CD 3 ; surveillance et gestion d’incident 3 ; documentation et soutenance 3. Ajuster le barème si le parcours avancé est obligatoire.

Exercices corrigés attendus : 1) une masse négative doit échouer au schéma ; 2) une cible dans les entrées est une fuite ; 3) un candidat échoué ne remplace pas le champion ; 4) un changement d’alias ne change pas un processus déjà chargé ; 5) une dérive de masse ne prouve pas une baisse du F1 ; 6) le vrai F1 exige des labels ; 7) restaurer une image doit restaurer le modèle et son prétraitement ; 8) une jointure historique ne doit pas regarder le futur.

Projet final : ajouter un autre modèle, comparer sans utiliser le test pour tous les réglages, documenter un seuil, simuler un incident et montrer le retour à une version connue. Les captures seules ne suffisent pas : fournir code, commandes et preuves reproductibles.




# 23 Exploitation limites et références

Avant un usage public : authentification adaptée, HTTPS, gestion des secrets, contrôle des accès aux registres, volumes sauvegardés, journaux centralisés, suivi des dépendances et procédures d’incident. Le service local charge des artefacts Python de confiance ; ne pas accepter un joblib fourni par un utilisateur.

Ne pas confondre : graine fixe et reproductibilité totale ; qualité sur test et fiabilité future ; sauvegarde et versionnement ; redémarrage et réentraînement ; feature store et base applicative ; données réelles et dérive simulée.

Dépannage : ModuleNotFoundError → vérifier l’interpréteur et l’environnement ; modèle absent → entraîner puis promouvoir ; 401 → vérifier la clé côté client et serveur ; 422 → lire les champs rejetés ; port occupé → arrêter le service concurrent ; dashboard vide → attendre les collectes et générer du trafic ; historique Feast vide → vérifier horodatages et matérialisation.

Références officielles consultées le 20 novembre 2026 :
• Palmer Penguins : https://allisonhorst.github.io/palmerpenguins/articles/intro.html
• scikit-learn : https://scikit-learn.org/stable/common_pitfalls.html
• Pandera : https://pandera.readthedocs.io/
• MLflow Registry : https://mlflow.org/docs/latest/ml/model-registry/workflow/
• DVC : https://doc.dvc.org/
• FastAPI : https://fastapi.tiangolo.com/
• Docker Compose : https://docs.docker.com/compose/
• GitHub Actions : https://docs.github.com/en/actions
• Evidently : https://docs.evidentlyai.com/
• Prometheus et Grafana : https://prometheus.io/docs/ et https://grafana.com/docs/
• Prefect : https://docs.prefect.io/v3/
• Kubernetes et Terraform : https://kubernetes.io/docs/ et https://registry.terraform.io/providers/hashicorp/kubernetes/
• Feast : https://docs.feast.dev/getting-started/quickstart

Les sources accompagnent les définitions ; les scores du TP proviennent de l’exécution locale. Les versions exactes et les parcours exécutés figurent dans VALIDATION.md. Les fichiers du dossier sont les sources complètes à modifier et tester.




# Annexe eco/common.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

from pathlib import Path
import hashlib, json, os
BASE = Path(__file__).resolve().parent.parent
NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
CATEGORICAL = ["island", "sex"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "species"
MODEL_NAME = "EcoSpecies"
def config():
    return json.loads((BASE / "config.json").read_text())
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tracking_uri():
    return os.getenv("MLFLOW_TRACKING_URI", "sqlite:///" + str(BASE / "mlflow.db"))
def save_json(path, payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))

```



# Annexe eco/data.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Contrat des données et prétraitement partagé train/inférence."""
import numpy as np
import pandas as pd
import pandera.pandas as pa
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .common import NUMERIC, CATEGORICAL, TARGET, config
RANGES={"bill_length_mm":(20,80),"bill_depth_mm":(5,35),"flipper_length_mm":(100,300),"body_mass_g":(1000,10000)}
def schema():
    columns={name:pa.Column(float, checks=pa.Check.in_range(*RANGES[name]), nullable=True, coerce=True) for name in NUMERIC}
    columns.update({"island":pa.Column(str,pa.Check.isin(["Biscoe","Dream","Torgersen"])),"sex":pa.Column(str,pa.Check.isin(["Male","Female"]),nullable=True),TARGET:pa.Column(str,pa.Check.isin(["Adelie","Chinstrap","Gentoo"]))})
    return pa.DataFrameSchema(columns,strict=True)
def read_validate(path):
    df=pd.read_csv(path)
    # Harmoniser la casse sans remplacer les valeurs absentes.
    if "sex" in df: df["sex"]=df["sex"].str.title()
    df=schema().validate(df,lazy=True)
    if df.isna().mean().max()>config()["max_missing_fraction"]:
        raise ValueError("Trop de valeurs manquantes")
    if len(df)<100 or df[TARGET].value_counts().min()<20:
        raise ValueError("Dataset trop petit ou classe insuffisante")
    return df

def normalize(frame):
    # Les valeurs JSON nulles deviennent NaN, comme lors de la lecture CSV.
    df=frame.copy()
    for col in NUMERIC:
        df[col]=pd.to_numeric(df[col],errors="raise")
    for col in CATEGORICAL:
        df[col]=df[col].astype(object).where(df[col].notna(),np.nan)
    return df

def preprocessor():
    numeric=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical=Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("encode",OneHotEncoder(handle_unknown="ignore",sparse_output=False))])
    return ColumnTransformer([("numeric",numeric,NUMERIC),("category",categorical,CATEGORICAL)])

```



# Annexe eco/validate.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

from .common import BASE, save_json, digest
from .data import read_validate

def main():
    df=read_validate(BASE/"data/penguins.csv")
    report={"rows":len(df),"sha256":digest(BASE/"data/penguins.csv"),"missing":df.isna().sum().to_dict(),"classes":df.species.value_counts().to_dict()}
    save_json(BASE/"reports/data_validation.json",report)
    print(report)
if __name__=="__main__":main()

```



# Annexe eco/train.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Comparer sur validation ; ouvrir le test une seule fois pour le candidat choisi."""
import json, platform
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from .data import read_validate, normalize, preprocessor
from .common import BASE, FEATURES, TARGET, MODEL_NAME, config, tracking_uri, save_json, digest

def main():
    cfg=config(); df=read_validate(BASE/"data/penguins.csv")
    X,y=normalize(df[FEATURES]),df[TARGET]
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.2,stratify=y,random_state=cfg["seed"])
    X_train,X_val,y_train,y_val=train_test_split(X_dev,y_dev,test_size=.25,stratify=y_dev,random_state=cfg["seed"])
    mlflow.set_tracking_uri(tracking_uri());mlflow.set_experiment("EcoSpecies")
    candidates={"logistic":LogisticRegression(max_iter=1000,random_state=42),"forest":RandomForestClassifier(n_estimators=120,min_samples_leaf=2,random_state=42)}
    baseline=Pipeline([("prep",preprocessor()),("classifier",DummyClassifier(strategy="most_frequent"))]).fit(X_train,y_train)
    baseline_f1=f1_score(y_val,baseline.predict(X_val),average="macro")
    results=[]
    for name, classifier in candidates.items():
        with mlflow.start_run(run_name=name) as run:
            model=Pipeline([("prep",preprocessor()),("classifier",classifier)])
            model.fit(X_train,y_train)
            score=f1_score(y_val,model.predict(X_val),average="macro")
            mlflow.log_params({"algorithm":name,"seed":cfg["seed"],"train_rows":len(X_train),"validation_rows":len(X_val)})
            mlflow.set_tags({"data_sha256":digest(BASE/"data/penguins.csv"),"config_sha256":digest(BASE/"config.json"),"python":platform.python_version()})
            mlflow.log_metrics({"validation_f1_macro":score,"baseline_validation_f1_macro":baseline_f1})
            info=mlflow.sklearn.log_model(model,name="model",serialization_format="cloudpickle",signature=infer_signature(X_train,model.predict(X_train)),input_example=X_train.head(2))
            results.append({"algorithm":name,"score":score,"run_id":run.info.run_id,"uri":info.model_uri,"model":model})
    best=max(results,key=lambda r:r["score"])
    # Le test n'est pas utilisé pour choisir entre les deux candidats.
    predictions=best["model"].predict(X_test)
    test_f1=f1_score(y_test,predictions,average="macro")
    passed=best["score"]>=cfg["min_validation_f1"] and best["score"]>baseline_f1 and test_f1>=cfg["min_test_f1"]
    with mlflow.start_run(run_id=best["run_id"]):
        mlflow.log_metrics({"test_f1_macro":test_f1,"test_accuracy":accuracy_score(y_test,predictions)})
        mlflow.set_tag("quality_gate", "passed" if passed else "failed")
    version=mlflow.register_model(best["uri"],MODEL_NAME)
    mlflow.MlflowClient().set_model_version_tag(MODEL_NAME,version.version,"quality_gate","passed" if passed else "failed")
    report={"version":str(version.version),"run_id":best["run_id"],"model_name":MODEL_NAME,"algorithm":best["algorithm"],"validation_f1":best["score"],"baseline_validation_f1":baseline_f1,"test_f1":test_f1,"passed":passed,"data_sha256":digest(BASE/"data/penguins.csv"),"test_report":classification_report(y_test,predictions,output_dict=True),"splits":{"train":len(X_train),"validation":len(X_val),"test":len(X_test)}}
    save_json(BASE/"reports/candidate.json",report)
    print(json.dumps({k:v for k,v in report.items() if k!="test_report"},indent=2))
    if not passed:raise RuntimeError("Candidat refusé ; champion inchangé")
    return report
if __name__=="__main__":main()

```



# Annexe eco/promote.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Promotion explicite et export d'un bundle avec version et provenance."""
import argparse, json, os
import joblib, mlflow, mlflow.sklearn
from .common import BASE, MODEL_NAME, tracking_uri, save_json

def main(version, rollback=False):
    mlflow.set_tracking_uri(tracking_uri()); client=mlflow.MlflowClient()
    mv=client.get_model_version(MODEL_NAME,str(version))
    if mv.tags.get("quality_gate")!="passed":
        raise ValueError("Cette version n'a pas passé le contrôle qualité")
    model=mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{version}")
    target=BASE/"artifacts";target.mkdir(exist_ok=True)
    # Export d'abord, alias ensuite : l'API charge une version figée au démarrage.
    temp=target/"champion.tmp"
    joblib.dump({"model":model,"version":str(version),"run_id":mv.run_id,"model_name":MODEL_NAME},temp)
    os.replace(temp,target/"champion.joblib")
    registered=client.get_registered_model(MODEL_NAME)
    old=registered.aliases.get("champion")
    if old and old!=str(version):client.set_registered_model_alias(MODEL_NAME,"previous",old)
    client.set_registered_model_alias(MODEL_NAME,"champion",str(version))
    save_json(target/"manifest.json",{"version":str(version),"run_id":mv.run_id,"previous":old})
    print(f"Champion version {version}. Redémarrer ou redéployer l'API.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--version",required=True);a=p.parse_args();main(a.version)

```



# Annexe eco/api.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""API de prédiction authentifiée, métriques techniques et journal SQLite."""
from contextlib import asynccontextmanager
from pathlib import Path
import json, os, secrets, sqlite3, time, uuid
import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from .common import BASE, FEATURES
from .data import normalize
BUNDLE=Path(os.getenv("MODEL_PATH",str(BASE/"artifacts/champion.joblib")))
LOG=Path(os.getenv("PREDICTION_DB",str(BASE/".state/predictions.db")))
COUNT=Counter("eco_predictions_total","Prédictions réussies")
LATENCY=Histogram("eco_prediction_seconds","Latence de prédiction",buckets=(.005,.01,.025,.05,.1,.25,.5,1))
ERRORS=Counter("eco_errors_total","Erreurs HTTP",["status"])
@asynccontextmanager
async def lifespan(app):
    if not os.getenv("API_KEY"):raise RuntimeError("Définir API_KEY avant de démarrer")
    app.state.bundle=joblib.load(BUNDLE)  # Artefact construit et vérifié localement.
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(LOG) as db:
        db.execute("CREATE TABLE IF NOT EXISTS predictions(request_id TEXT PRIMARY KEY, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, model_version TEXT, features TEXT, prediction TEXT)")
    yield
app=FastAPI(title="EcoSpecies API",version="1.0.0",lifespan=lifespan)
class Penguin(BaseModel):
    model_config=ConfigDict(extra="forbid",allow_inf_nan=False)
    bill_length_mm:float|None=Field(default=None,ge=20,le=80)
    bill_depth_mm:float|None=Field(default=None,ge=5,le=35)
    flipper_length_mm:float|None=Field(default=None,ge=100,le=300)
    body_mass_g:float|None=Field(default=None,ge=1000,le=10000)
    island:str=Field(pattern="^(Biscoe|Dream|Torgersen)$")
    sex:str|None=Field(default=None,pattern="^(Male|Female)$")
def auth(x_api_key:str|None=Header(default=None)):
    if not secrets.compare_digest(x_api_key or "",os.environ.get("API_KEY","")):
        raise HTTPException(401,"Clé absente ou invalide")
@app.middleware("http")
async def count_errors(request,call_next):
    response=await call_next(request)
    if response.status_code>=400:ERRORS.labels(status=str(response.status_code)).inc()
    return response
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/ready")
def ready():return {"ready":True,"model_version":app.state.bundle["version"]}
@app.get("/metrics",include_in_schema=False)
def metrics():return Response(content=generate_latest(),headers={"Content-Type":CONTENT_TYPE_LATEST})
@app.post("/api/v1/predict",dependencies=[Depends(auth)])
def predict(values:Penguin):
    started=time.perf_counter();features=values.model_dump()
    if all(features[k] is None for k in FEATURES[:4]):raise HTTPException(422,"Au moins une mesure physique est requise")
    frame=normalize(pd.DataFrame([features],columns=FEATURES))
    bundle=app.state.bundle;prediction=str(bundle["model"].predict(frame)[0]);rid=str(uuid.uuid4())
    with sqlite3.connect(LOG) as db:
        db.execute("INSERT INTO predictions(request_id,model_version,features,prediction) VALUES(?,?,?,?)",(rid,bundle["version"],json.dumps(features),prediction))
    COUNT.inc();LATENCY.observe(time.perf_counter()-started)
    return {"request_id":rid,"species":prediction,"model_version":bundle["version"]}

```



# Annexe tests/test_system.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

import os, joblib
import numpy as np, pandas as pd, pytest
from fastapi.testclient import TestClient
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from eco.common import BASE, FEATURES
from eco.data import read_validate, normalize, preprocessor
from eco.api import app

def test_data_contract():
    df=read_validate(BASE/"data/penguins.csv")
    assert len(df)==344 and set(df.species)=={"Adelie","Gentoo","Chinstrap"}
def test_invalid_data(tmp_path):
    df=pd.read_csv(BASE/"data/penguins.csv");df.loc[0,"body_mass_g"]=-1
    f=tmp_path/"bad.csv";df.to_csv(f,index=False)
    with pytest.raises(Exception):read_validate(f)
def test_pipeline_and_missing():
    df=read_validate(BASE/"data/penguins.csv")
    model=Pipeline([("prep",preprocessor()),("model",LogisticRegression(max_iter=1000))]).fit(normalize(df[FEATURES]),df.species)
    row=df[FEATURES].iloc[:1].copy();row.loc[row.index[0],"sex"]=None
    assert model.predict(normalize(row))[0] in model.classes_
def test_api(monkeypatch,tmp_path):
    import eco.api as api
    df=read_validate(BASE/"data/penguins.csv")
    model=Pipeline([("prep",preprocessor()),("model",LogisticRegression(max_iter=1000))]).fit(normalize(df[FEATURES]),df.species)
    f=tmp_path/"model.joblib";joblib.dump({"model":model,"version":"test"},f)
    monkeypatch.setattr(api,"BUNDLE",f);monkeypatch.setattr(api,"LOG",tmp_path/"logs.db");monkeypatch.setenv("API_KEY","unit-test-only")
    body={"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750,"island":"Torgersen","sex":"Male"}
    with TestClient(app) as client:
        assert client.get("/health").status_code==200
        assert client.post("/api/v1/predict",json=body).status_code==401
        headers={"X-API-Key":"unit-test-only"}
        r=client.post("/api/v1/predict",json=body,headers=headers)
        assert r.status_code==200 and r.json()["model_version"]=="test"
        assert client.post("/api/v1/predict",json={**body,"body_mass_g":-1},headers=headers).status_code==422
        assert "eco_predictions_total" in client.get("/metrics").text

```



# Annexe eco/monitor.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Dérive simulée et vraie qualité uniquement si les labels sont disponibles."""
import argparse,json
import numpy as np,pandas as pd
from scipy.stats import ks_2samp
from evidently import Report
from evidently.presets import DataDriftPreset
from sklearn.metrics import f1_score
from .common import BASE, NUMERIC, save_json

def main(current=None):
    reference=pd.read_csv(BASE/"data/penguins.csv")[NUMERIC].dropna()
    if current:
        observed=pd.read_csv(current)[NUMERIC].dropna(); simulated=False
    else:
        observed=reference.sample(n=150,random_state=7).copy()
        observed["body_mass_g"]+=1200;simulated=True
    if min(len(reference),len(observed))<50:raise ValueError("Au moins 50 observations par groupe")
    # Rapport Evidently autonome ; résultat statistique != preuve de baisse de qualité.
    snapshot=Report([DataDriftPreset()]).run(current_data=observed,reference_data=reference)
    (BASE/"reports").mkdir(exist_ok=True)
    snapshot.save_html(str(BASE/"reports/drift.html"))
    pvalues={c:float(ks_2samp(reference[c],observed[c]).pvalue) for c in NUMERIC}
    threshold=.01/len(NUMERIC)  # Bonferroni pour les 4 comparaisons de ce TP.
    save_json(BASE/"reports/drift.json",{"simulated":simulated,"ks_pvalues":pvalues,"threshold":threshold,"alert":any(p<threshold for p in pvalues.values()),"performance_known":False})
    print("Rapport reports/drift.html ; données simulées" if simulated else "Rapport sur le CSV fourni")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--current");a=p.parse_args();main(a.current)

```



# Annexe eco/evaluate_logs.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Rattache des labels réels au journal ; n'invente pas les réponses correctes."""
import argparse, sqlite3
import pandas as pd
from sklearn.metrics import f1_score
from .api import LOG
from .common import BASE, save_json

def main(labels_path):
    labels=pd.read_csv(labels_path,dtype={"request_id":str})
    if labels.request_id.duplicated().any():raise ValueError("request_id dupliqué dans les labels")
    if not set(labels.species).issubset({"Adelie","Gentoo","Chinstrap"}):raise ValueError("Espèce invalide")
    with sqlite3.connect(LOG) as db:pred=pd.read_sql_query("SELECT request_id,model_version,prediction FROM predictions",db)
    merged=pred.merge(labels,on="request_id",validate="one_to_one")
    if merged.empty:raise ValueError("Aucun label correspondant")
    scores={str(v):{"rows":len(g),"f1_macro":float(f1_score(g.species,g.prediction,average="macro",labels=["Adelie","Chinstrap","Gentoo"],zero_division=0))} for v,g in merged.groupby("model_version")}
    save_json(BASE/"reports/performance.json",{"coverage":len(merged)/max(len(pred),1),"by_model":scores})
    print(scores)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--labels",required=True);a=p.parse_args();main(a.labels)

```



# Annexe eco/flow.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

"""Orchestration CT : le réentraînement ne promeut jamais automatiquement."""
from prefect import flow, task
from .validate import main as validate
from .train import main as train
@task(retries=1,retry_delay_seconds=2)
def validate_task():
    return validate()
@task(retries=0)
def train_task():
    # Pas de retry automatique : éviter des doublons d'expériences/versions.
    return train()
@flow(name="ecospecies-training",log_prints=True)
def pipeline():
    validate_task()
    return train_task()
if __name__=="__main__":pipeline()

```



# Annexe Dockerfile

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

FROM python:3.12-slim
WORKDIR /app
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt
COPY eco ./eco
COPY config.json .
COPY artifacts/champion.joblib ./artifacts/champion.joblib
RUN useradd --uid 10001 --create-home appuser && mkdir /app/.state && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["python","-m","uvicorn","eco.api:app","--host","0.0.0.0","--port","8000"]

```



# Annexe compose.yaml

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

services:
  api:
    build: .
    environment:
      API_KEY: ${API_KEY:?Définir API_KEY}
    ports: ["127.0.0.1:8000:8000"]
    volumes: ["api-state:/app/.state"]
  prometheus:
    image: prom/prometheus:v3.2.1
    command: ["--config.file=/etc/prometheus/prometheus.yml"]
    volumes: ["./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro", "prom-data:/prometheus"]
    ports: ["127.0.0.1:9090:9090"]
    depends_on: [api]
  grafana:
    image: grafana/grafana:11.6.0
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:?Définir GRAFANA_PASSWORD}
    volumes: ["./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro", "./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro", "grafana-data:/var/lib/grafana"]
    ports: ["127.0.0.1:3000:3000"]
    depends_on: [prometheus]
volumes:
  api-state:
  prom-data:
  grafana-data:

```



# Annexe monitoring/prometheus.yml

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

global:
  scrape_interval: 10s
scrape_configs:
  - job_name: ecospecies
    static_configs:
      - targets: ["api:8000"]

```



# Annexe .github/workflows/ci.yml

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

name: CI et construction image
on:
  push:
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
  packages: write
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m pip install -r requirements-lock.txt
      - run: python -m eco.validate
      - run: python -m pytest -q
      - run: python -m eco.train
      - name: Promouvoir dans cet environnement CI isolé
        run: |
          VERSION=$(python -c 'import json; print(json.load(open("reports/candidate.json"))["version"])')
          python -m eco.promote --version "$VERSION"
      - run: docker build -t ecospecies:ci .
      - uses: actions/upload-artifact@v4
        with:
          name: evaluation
          path: reports/
      - name: Publier une image immuable sur demande
        if: github.event_name == 'workflow_dispatch'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          IMAGE="ghcr.io/${GITHUB_REPOSITORY,,}:${GITHUB_SHA}"
          printf '%s' "$GH_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
          docker tag ecospecies:ci "$IMAGE"
          docker push "$IMAGE"

```



# Annexe .github/workflows/deploy.yml

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

name: CD Kubernetes local contrôlé
on:
  workflow_dispatch:
    inputs:
      image:
        description: Image publique GHCR avec tag SHA ou digest
        required: true
        type: string
permissions:
  contents: read
jobs:
  deploy:
    runs-on: self-hosted
    environment: classroom
    steps:
      - uses: actions/checkout@v4
      - name: Déployer dans le cluster déjà préparé
        env:
          IMAGE: ${{ inputs.image }}
        run: |
          kubectl -n ecospecies set image deployment/ecospecies api="$IMAGE"
          kubectl -n ecospecies rollout status deployment/ecospecies --timeout=120s
          kubectl -n ecospecies get pods

```



# Annexe infra/main.tf

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```text

terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }
}
variable "kubeconfig_path" {
  type = string
  default = "~/.kube/config"
}
variable "image" {
  type = string
  default = "ecospecies:classroom"
}
variable "api_key" {
  type = string
  sensitive = true
}
provider "kubernetes" {
  config_path = pathexpand(var.kubeconfig_path)
  config_context = "kind-ecospecies"
}
resource "kubernetes_namespace_v1" "eco" {
  metadata { name = "ecospecies" }
}
resource "kubernetes_secret_v1" "auth" {
  metadata {
    name = "eco-auth"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  data = { API_KEY = var.api_key }
}
resource "kubernetes_deployment_v1" "api" {
  metadata {
    name = "ecospecies"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "ecospecies" } }
    template {
      metadata { labels = { app = "ecospecies" } }
      spec {
        security_context {
          run_as_non_root = true
          run_as_user = 10001
          fs_group = 10001
        }
        container {
          name = "api"
          image = var.image
          image_pull_policy = "IfNotPresent"
          port { container_port = 8000 }
          env {
            name = "API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.auth.metadata[0].name
                key = "API_KEY"
              }
            }
          }
          resources {
            requests = { cpu = "100m", memory = "256Mi" }
            limits = { cpu = "1", memory = "1Gi" }
          }
          readiness_probe {
            http_get {
              path = "/ready"
              port = 8000
            }
            initial_delay_seconds = 15
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
          }
        }
      }
    }
  }
}
resource "kubernetes_service_v1" "api" {
  metadata {
    name = "ecospecies"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  spec {
    selector = { app = "ecospecies" }
    port {
      port = 8000
      target_port = 8000
    }
  }
}

```



# Annexe feast_repo/features.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Float64, String
observation=Entity(name="observation",join_keys=["observation_id"])
source=FileSource(path="observations.parquet",timestamp_field="event_timestamp")
measurements=FeatureView(name="measurements",entities=[observation],ttl=timedelta(days=365),schema=[Field(name=n,dtype=Float64) for n in ["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]]+[Field(name="island",dtype=String),Field(name="sex",dtype=String)],source=source)
service=FeatureService(name="penguin_features",features=[measurements])

```



# Annexe feast_repo/prepare.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

def main():
    """Dates de disponibilité fictives pour le TP ; aucun label dans la feature view."""
    from pathlib import Path
    import pandas as pd
    base=Path(__file__).resolve().parent
    frame=pd.read_csv(base.parent/"data/penguins.csv").dropna().reset_index(drop=True)
    frame["sex"]=frame["sex"].str.title()
    frame["observation_id"]=frame.index.astype(str)
    frame["event_timestamp"]=pd.Timestamp.now(tz="UTC")-pd.Timedelta(days=1)
    frame.drop(columns=["species"]).to_parquet(base/"observations.parquet",index=False)
    frame[["observation_id","event_timestamp"]].head(5).to_parquet(base/"entities.parquet",index=False)
    print("Source préparée ; horodatages de démonstration")

if __name__ == "__main__":
    main()

```



# Annexe feast_repo/client.py

Code source complet du fichier fourni. Les commentaires relient les instructions aux notions du cours.

```python

def main():
    import json, os
    import pandas as pd, requests
    from feast import FeatureStore
    store=FeatureStore(repo_path=".")
    service=store.get_feature_service("penguin_features")
    # Jointure historique point-in-time ; mêmes noms de caractéristiques qu'en ligne.
    entities=pd.read_parquet("entities.parquet")
    historical=store.get_historical_features(entity_df=entities,features=service).to_df()
    print("Historique",historical.shape)
    features=store.get_online_features(features=service,entity_rows=[{"observation_id":"0"}]).to_dict()
    values={k:v[0] for k,v in features.items() if k!="observation_id"}
    if any(v is None for v in values.values()):raise RuntimeError("Valeurs non matérialisées")
    print(json.dumps(values,indent=2))
    if os.getenv("API_KEY"):
        r=requests.post("http://127.0.0.1:8000/api/v1/predict",json=values,headers={"X-API-Key":os.environ["API_KEY"]},timeout=20)
        r.raise_for_status();print(r.json())

if __name__ == "__main__":
    main()

```

