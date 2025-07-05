# API MSPR-TPRE-601 : Documentation Complète

## 📋 Sommaire

1. [Vue d'ensemble](#vue-d-ensemble)
2. [Architecture Technique](#architecture-technique)
3. [Installation et Configuration](#installation-et-configuration)
4. [Structure du Projet](#structure-du-projet)
5. [Documentation des Contrôleurs](#documentation-des-contrôleurs)
6. [Documentation des Tests](#documentation-des-tests)
7. [Configuration Pylint](#configuration-pylint)
8. [Plan de Tests](#plan-de-tests)
9. [Déploiement Docker](#déploiement-docker)
10. [API Documentation](#api-documentation)
11. [Sécurité](#sécurité)
12. [Monitoring et Logs](#monitoring-et-logs)
13. [Maintenance](#maintenance)

---

## 🚀 Vue d'ensemble

### Description du Projet

L'API MSPR-TPRE-601 est une application Flask moderne développée pour la gestion de données de santé et climatiques. Elle fournit une interface REST complète pour :

- **Gestion des utilisateurs** : authentification, autorisation, CRUD
- **Données géographiques** : continents, pays, régions, villes
- **Données climatiques** : types de climat, rapports météorologiques
- **Données de santé** : maladies, prédictions, statistiques
- **Monitoring** : logs, métriques, surveillance

### Fonctionnalités Principales

- ✅ **Authentification JWT** : Sécurisation des endpoints
- ✅ **Documentation Swagger** : Interface interactive pour tester l'API
- ✅ **Base de données PostgreSQL** : Stockage persistant des données
- ✅ **Tests automatisés** : Couverture de code avec pytest
- ✅ **Qualité de code** : Analyse avec pylint
- ✅ **Conteneurisation** : Déploiement avec Docker
- ✅ **CORS** : Support multi-origine
- ✅ **Monitoring** : Logs et métriques intégrés

### Technologies Utilisées

- **Backend** : Flask 3.0.3, Flask-RESTX 1.3.0
- **Base de données** : PostgreSQL avec psycopg2-binary
- **Sécurité** : JWT, bcrypt pour le hachage des mots de passe
- **Tests** : pytest, pytest-cov, pytest-mock
- **Qualité** : pylint 3.1.0
- **Déploiement** : Docker, gunicorn
- **Configuration** : python-dotenv pour les variables d'environnement

---

## 🏗️ Architecture Technique

### Diagramme d'Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Flask     │    │   PostgreSQL    │
│   (Client)      │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Docker        │
                       │   Container     │
                       └─────────────────┘
```

### Architecture Modulaire

```
app.py (Point d'entrée)
├── controller/ (Logique métier)
│   ├── login_controller.py
│   ├── prediction_controller.py
│   ├── disease_controller.py
│   └── ... (autres contrôleurs)
├── connect_db.py (Connexion DB)
├── tests/ (Tests automatisés)
└── assets/bruno/ (Tests API)
```

### Flux de Données

1. **Requête Client** → API Flask
2. **Validation** → JWT Token (si requis)
3. **Contrôleur** → Logique métier
4. **Base de données** → PostgreSQL
5. **Réponse** → JSON formaté

---

## 🛠️ Installation et Configuration

### Prérequis

- Python 3.9+
- PostgreSQL 12+
- Docker (optionnel)
- Git

### Installation Locale

```bash
# Cloner le repository
git clone <repository-url>
cd MSPR-TPRE-601-API

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration Base de Données

1. **Créer le fichier `.env`** :
```env
DB_HOST=localhost
DB_DATABASE=mspr_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

2. **Initialiser la base de données** :
```sql
-- Créer la base de données
CREATE DATABASE mspr_db;

-- Connecter à la base
\c mspr_db;

-- Créer les tables nécessaires
-- (Schéma disponible dans le dossier sql/)
```

### Lancement de l'Application

```bash
# Mode développement
python app.py

# Mode production
gunicorn -b 0.0.0.0:5000 app:app
```

L'API sera accessible sur `http://localhost:5000`

---

## 📁 Structure du Projet

```
MSPR-TPRE-601-API/
├── app.py                    # Point d'entrée principal
├── connect_db.py            # Gestion connexion DB
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Configuration Docker
├── pylintrc                # Configuration pylint
├── pytest.ini             # Configuration pytest
├── README.md               # Documentation
├── __init__.py             # Module Python
│
├── controller/             # Contrôleurs API
│   ├── __init__.py
│   ├── login_controller.py      # Authentification
│   ├── prediction_controller.py # Prédictions
│   ├── disease_controller.py    # Maladies
│   ├── country_controller.py    # Pays
│   ├── region_controller.py     # Régions
│   ├── continent_controller.py  # Continents
│   ├── climat_type_controller.py # Types climat
│   ├── statement_controller.py  # Déclarations
│   ├── metric_controller.py     # Métriques
│   └── log_controller.py        # Logs
│
├── tests/                  # Tests automatisés
│   ├── __init__.py
│   ├── conftest.py         # Configuration pytest
│   ├── test_app.py         # Tests application
│   ├── test_connect_db.py  # Tests connexion DB
│   ├── test_integration.py # Tests intégration
│   └── test_*_controller.py # Tests contrôleurs
│
└── assets/                 # Ressources
    └── bruno/              # Tests API Bruno
        ├── collection.bru
        ├── environments/
        └── */              # Tests par endpoint
```

---

## 🎮 Documentation des Contrôleurs

### Structure d'un Contrôleur

Chaque contrôleur suit le pattern suivant :

```python
# 1. Imports et namespace
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from connect_db import DBConnection

# 2. Définition du namespace
namespace = Namespace('entity', description="Description")

# 3. Modèles Swagger
model = namespace.model('Entity', {
    'id': fields.Integer(description='ID unique'),
    'name': fields.String(description='Nom')
})

# 4. Routes et méthodes
@namespace.route('/entities')
class EntityListResource(Resource):
    @jwt_required()
    @namespace.marshal_list_with(model)
    def get(self):
        # Logique GET
        pass
```

### Contrôleurs Disponibles

#### 1. Login Controller (`login_controller.py`)

**Fonctionnalités** :
- Authentification utilisateur
- Création, lecture, modification, suppression d'utilisateurs
- Gestion des rôles administrateur

**Endpoints** :
- `POST /swagger/user/users/login` - Authentification
- `GET /swagger/user/users` - Liste des utilisateurs (admin)
- `POST /swagger/user/users` - Création utilisateur
- `GET /swagger/user/users/{id}` - Détails utilisateur
- `PUT /swagger/user/users/{id}` - Modification utilisateur
- `DELETE /swagger/user/users/{id}` - Suppression utilisateur

**Sécurité** :
- Hachage bcrypt des mots de passe
- Tokens JWT avec expiration (2h)
- Vérification des droits administrateur

#### 2. Prediction Controller (`prediction_controller.py`)

**Fonctionnalités** :
- Prédictions épidémiologiques
- Calcul des taux de mortalité et transmission
- Analyse statistique par région

**Endpoints** :
- `GET /swagger/predictions/get` - Prédictions générales
- `POST /swagger/predictions/mortality-rate` - Taux de mortalité
- `POST /swagger/predictions/transmission-rate` - Taux de transmission

#### 3. Disease Controller (`disease_controller.py`)

**Fonctionnalités** :
- Gestion des maladies
- CRUD complet sur les maladies
- Liaison avec les données climatiques

**Endpoints** :
- `GET /swagger/diseases` - Liste des maladies
- `POST /swagger/diseases` - Création maladie
- `GET /swagger/diseases/{id}` - Détails maladie
- `PUT /swagger/diseases/{id}` - Modification maladie
- `DELETE /swagger/diseases/{id}` - Suppression maladie

#### 4. Geographic Controllers

**Country Controller** :
- Gestion des pays
- Liaison avec continents et régions
- Données climatiques par pays

**Region Controller** :
- Gestion des régions
- Hiérarchie géographique
- Statistiques régionales

**Continent Controller** :
- Gestion des continents
- Vue d'ensemble géographique

#### 5. Climate Controllers

**Climat Type Controller** :
- Types de climat
- Classifications climatiques
- Données météorologiques

#### 6. Monitoring Controllers

**Log Controller** :
- Gestion des logs système
- Consultation des logs par pays
- Métriques d'utilisation

**Metric Controller** :
- Métriques de performance
- Statistiques d'utilisation
- Monitoring temps réel

---

## 🧪 Documentation des Tests

### Configuration des Tests

**Fichier `pytest.ini`** :
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
    --verbose
    -ra
```

### Structure des Tests

#### 1. Test de Configuration (`conftest.py`)

**Fixtures disponibles** :
- `app` : Instance Flask pour les tests
- `client` : Client de test Flask
- `jwt_token` : Token JWT pour les tests authentifiés
- `mock_db` : Mock de la base de données

#### 2. Tests Unitaires

**Test App (`test_app.py`)** :
- Test de la route racine
- Test des endpoints protégés
- Test de la configuration JWT
- Test des messages d'erreur

**Test Connection DB (`test_connect_db.py`)** :
- Test de connexion réussie
- Test de gestion des erreurs
- Test du gestionnaire de contexte
- Test des variables d'environnement

#### 3. Tests d'Intégration (`test_integration.py`)

**Couverture** :
- Tests end-to-end des endpoints
- Test des flux complets
- Test des réponses d'erreur
- Test de la documentation Swagger

#### 4. Tests des Contrôleurs

**Chaque contrôleur a son fichier de test** :
- `test_login_controller.py` : Tests authentification
- `test_prediction_controller.py` : Tests prédictions
- `test_disease_controller.py` : Tests maladies
- `test_country_controller.py` : Tests pays
- `test_log_controller.py` : Tests logs

**Pattern de test** :
```python
class TestEntityController:
    def test_get_entities_success(self, client, jwt_token):
        # Test récupération réussie
        pass
    
    def test_create_entity_success(self, client, jwt_token):
        # Test création réussie
        pass
    
    def test_entity_not_found(self, client, jwt_token):
        # Test erreur 404
        pass
    
    def test_unauthorized_access(self, client):
        # Test accès non autorisé
        pass
```

### Commandes de Test

```bash
# Exécuter tous les tests
pytest

# Tests avec couverture
pytest --cov=controller

# Tests spécifiques
pytest tests/test_login_controller.py

# Tests en mode verbose
pytest -v

# Générer rapport HTML
pytest --cov=controller --cov-report=html
```

### Métriques de Qualité

**Objectifs de couverture** :
- Couverture minimale : 80%
- Couverture ciblée : 90%+
- Tests critiques : 100%

**Types de tests** :
- **Unitaires** : 70% des tests
- **Intégration** : 20% des tests
- **End-to-end** : 10% des tests

---

## 🔍 Configuration Pylint

### Configuration Principale

Le fichier `pylintrc` contient une configuration détaillée pour maintenir la qualité du code :

**Standards de nommage** :
- `snake_case` pour les variables et fonctions
- `PascalCase` pour les classes
- `UPPER_CASE` pour les constantes

**Règles désactivées** :
- `too-few-public-methods` : Classes avec peu de méthodes
- `import-outside-toplevel` : Imports dynamiques
- `line-too-long` : Lignes dépassant 100 caractères

**Seuils de qualité** :
- Score minimum : 8.0/10
- Erreurs bloquantes : 0
- Warnings maximum : 10

### Commandes Pylint

```bash
# Analyser tout le projet
pylint *.py controller/ tests/

# Analyser un fichier spécifique
pylint app.py

# Rapport détaillé
pylint --reports=y controller/

# Format JSON
pylint --output-format=json controller/ > pylint_report.json
```

### Métriques Pylint

**Indicateurs surveillés** :
- **Score global** : > 8.0/10
- **Erreurs** : 0 toléré
- **Warnings** : < 10
- **Conventions** : 100% respect
- **Duplications** : < 5%

---

## 📋 Plan de Tests

### Stratégie de Test

#### 1. Tests Unitaires (70%)

**Objectifs** :
- Tester chaque fonction isolément
- Vérifier la logique métier
- Valider les cas d'erreur

**Couverture** :
- Contrôleurs : 100% des méthodes
- Utilitaires : 100% des fonctions
- Modèles : 100% des validations

#### 2. Tests d'Intégration (20%)

**Objectifs** :
- Tester les interactions entre composants
- Vérifier les flux de données
- Valider les réponses API

**Couverture** :
- Endpoints API : 100%
- Authentification : 100%
- Base de données : 100%

#### 3. Tests End-to-End (10%)

**Objectifs** :
- Tester les scénarios utilisateur complets
- Vérifier les performances
- Valider l'expérience utilisateur

**Couverture** :
- Workflows critiques : 100%
- Cas d'usage principaux : 100%

### Scénarios de Test

#### Scénarios Critiques

1. **Authentification** :
   - Login avec identifiants valides
   - Login avec identifiants invalides
   - Expiration de token
   - Tentatives de force brute

2. **Gestion des Données** :
   - Création d'entités
   - Modification d'entités
   - Suppression d'entités
   - Récupération d'entités

3. **Sécurité** :
   - Accès non autorisé
   - Injection SQL
   - Validation des données
   - Gestion des erreurs

#### Scénarios de Performance

1. **Charge** :
   - 100 utilisateurs simultanés
   - 1000 requêtes/seconde
   - Temps de réponse < 200ms

2. **Disponibilité** :
   - Uptime > 99.9%
   - Récupération après panne
   - Failover automatique

### Exécution des Tests

#### Pipeline CI/CD

```yaml
# GitHub Actions / GitLab CI
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=controller --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

#### Tests Locaux

```bash
# Configuration de test
export DB_HOST=localhost
export DB_DATABASE=mspr_test_db
export DB_USER=test_user
export DB_PASSWORD=test_password
export DB_PORT=5432

# Exécution des tests
pytest tests/ -v --cov=controller --cov-report=html

# Tests spécifiques
pytest tests/test_login_controller.py::TestLoginController::test_login_success
```

---

## 🐳 Déploiement Docker

### Configuration Docker

**Dockerfile** :
```dockerfile
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

EXPOSE 5000

# Lancement en production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Commandes Docker

```bash
# Construction de l'image
docker build -t mspr-601-api .

# Lancement du conteneur
docker run -d \
  --name mspr-api \
  -p 5000:5000 \
  -e DB_HOST=host.docker.internal \
  -e DB_DATABASE=mspr_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -e DB_PORT=5432 \
  mspr-601-api

# Lancement en mode développement
docker run -d \
  --name mspr-api-dev \
  -p 5001:5000 \
  -v $(pwd):/app \
  mspr-601-api \
  python3 /app/app.py
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=postgres
      - DB_DATABASE=mspr_db
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_PORT=5432
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=mspr_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Déploiement en Production

```bash
# Avec Docker Compose
docker-compose up -d

# Vérification du statut
docker-compose ps

# Consultation des logs
docker-compose logs -f api

# Mise à jour
docker-compose pull
docker-compose up -d
```

---

## 📚 API Documentation

### Accès à la Documentation

**Swagger UI** : `http://localhost:5000/api/docs`

### Authentification

Toutes les routes (sauf login) nécessitent un token JWT :

```bash
# Obtenir un token
curl -X POST http://localhost:5000/swagger/user/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Utiliser le token
curl -X GET http://localhost:5000/swagger/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Endpoints Principaux

#### Authentification
- `POST /swagger/user/users/login` - Connexion
- `GET /swagger/user/users` - Liste des utilisateurs
- `POST /swagger/user/users` - Création d'utilisateur

#### Données Géographiques
- `GET /swagger/continents` - Liste des continents
- `GET /swagger/countries` - Liste des pays
- `GET /swagger/regions` - Liste des régions

#### Données de Santé
- `GET /swagger/diseases` - Liste des maladies
- `POST /swagger/predictions/mortality-rate` - Taux de mortalité
- `POST /swagger/predictions/transmission-rate` - Taux de transmission

#### Monitoring
- `GET /swagger/logs` - Logs système
- `GET /swagger/metrics` - Métriques

### Exemples d'Utilisation

#### Authentification
```bash
# Login
curl -X POST http://localhost:5000/swagger/user/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'

# Réponse
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Récupération des Données
```bash
# Liste des pays
curl -X GET http://localhost:5000/swagger/countries \
  -H "Authorization: Bearer YOUR_TOKEN"

# Réponse
[
  {
    "id_country": 1,
    "name": "France",
    "continent": "Europe",
    "population": 67000000
  }
]
```

---

## 🔒 Sécurité

### Authentification JWT

**Configuration** :
- Algorithme : HS256
- Durée de vie : 2 heures
- Clé secrète : configurée dans l'environnement

**Implémentation** :
```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

# Configuration JWT
app.config['JWT_SECRET_KEY'] = 'your_super_secure_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
jwt = JWTManager(app)

# Création de token
access_token = create_access_token(identity=str(user_id))

# Protection d'endpoint
@jwt_required()
def protected_route():
    current_user = get_jwt_identity()
    return {"user": current_user}
```

### Hachage des Mots de Passe

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### Protection contre les Attaques

1. **Injection SQL** :
   - Utilisation de requêtes préparées
   - Validation des entrées
   - Échappement des caractères spéciaux

2. **CORS** :
   - Configuration Flask-CORS
   - Restriction des origines
   - Gestion des headers

3. **Validation des Données** :
   - Modèles Swagger
   - Validation des types
   - Sanitisation des entrées

### Bonnes Pratiques

1. **Variables d'Environnement** :
   - Secrets dans `.env`
   - Pas de credentials dans le code
   - Configuration par environnement

2. **Logs de Sécurité** :
   - Tentatives de connexion
   - Accès non autorisés
   - Erreurs de validation

3. **Monitoring** :
   - Surveillance des endpoints
   - Détection d'anomalies
   - Alertes automatiques

---

## 📊 Monitoring et Logs

### Système de Logs

**Configuration** :
```python
import logging
from datetime import datetime

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Log Controller

**Fonctionnalités** :
- Récupération des logs par pays
- Filtrage par date
- Métriques d'utilisation
- Monitoring temps réel

**Endpoints** :
```python
@log_namespace.route('/logs')
def get_logs():
    # Récupération des logs
    pass

@log_namespace.route('/logs/<int:country_id>')
def get_logs_by_country(country_id):
    # Logs par pays
    pass
```

### Métriques

**Indicateurs surveillés** :
- Nombre de requêtes par endpoint
- Temps de réponse moyen
- Taux d'erreur
- Utilisation des ressources

**Collecte des Métriques** :
```python
from time import time

def track_request_metrics(func):
    def wrapper(*args, **kwargs):
        start_time = time()
        try:
            result = func(*args, **kwargs)
            status = 'success'
            return result
        except Exception as e:
            status = 'error'
            raise e
        finally:
            duration = time() - start_time
            log_metric(func.__name__, duration, status)
    return wrapper
```

### Alertes

**Conditions d'alerte** :
- Taux d'erreur > 5%
- Temps de réponse > 2 secondes
- Utilisation CPU > 80%
- Utilisation mémoire > 85%

---

## 🛠️ Maintenance

### Tâches de Maintenance

#### Quotidiennes
- Vérification des logs d'erreur
- Contrôle des métriques de performance
- Sauvegarde de la base de données

#### Hebdomadaires
- Nettoyage des logs anciens
- Mise à jour des dépendances
- Analyse des performances

#### Mensuelles
- Audit de sécurité
- Optimisation des requêtes
- Révision de la documentation

### Procédures de Mise à Jour

```bash
# 1. Sauvegarde
pg_dump mspr_db > backup_$(date +%Y%m%d).sql

# 2. Tests
pytest tests/

# 3. Déploiement
docker-compose down
docker-compose pull
docker-compose up -d

# 4. Vérification
curl -f http://localhost:5000/ || exit 1
```

### Monitoring de Production

**Outils recommandés** :
- **Prometheus** : Collecte de métriques
- **Grafana** : Visualisation
- **ELK Stack** : Gestion des logs
- **Sentry** : Monitoring des erreurs

**Configuration Prometheus** :
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mspr-api'
    static_configs:
      - targets: ['localhost:5000']
```

---

## 🤝 Contribution

### Standards de Développement

1. **Style de Code** :
   - PEP 8 pour Python
   - Docstrings pour toutes les fonctions
   - Type hints quand possible

2. **Tests** :
   - Couverture minimale 80%
   - Tests unitaires pour nouvelle fonctionnalité
   - Tests d'intégration pour nouveaux endpoints

3. **Documentation** :
   - Mise à jour du README
   - Documentation Swagger
   - Commentaires pour la logique complexe

### Processus de Contribution

1. **Fork** du repository
2. **Branche** pour la fonctionnalité
3. **Développement** avec tests
4. **Pull Request** avec description
5. **Code Review** par l'équipe
6. **Merge** après validation

### Outils de Développement

```bash
# Configuration pré-commit
pre-commit install

# Formatage du code
black *.py controller/ tests/

# Analyse statique
pylint *.py controller/ tests/

# Tests avant commit
pytest tests/ --cov=controller
```

---

## 📞 Support

### Contacts

- **Équipe de développement** : dev@mspr.com
- **Support technique** : support@mspr.com
- **Documentation** : docs@mspr.com

### Ressources

- **Repository** : https://github.com/mspr/601-api
- **Documentation** : https://docs.mspr.com/601-api
- **Issues** : https://github.com/mspr/601-api/issues

### FAQ

**Q : Comment obtenir un token JWT ?**
R : Utilisez l'endpoint `/swagger/user/users/login` avec vos identifiants.

**Q : Quelle est la durée de vie d'un token ?**
R : Les tokens expirent au bout de 2 heures.

**Q : Comment ajouter un nouvel endpoint ?**
R : Créez une nouvelle méthode dans le contrôleur approprié avec les décorateurs Swagger.

---

## 📝 Changelog

### Version 1.0.0 (2024-01-15)
- ✅ Authentification JWT
- ✅ Documentation Swagger
- ✅ Tests automatisés
- ✅ Déploiement Docker
- ✅ Monitoring et logs

### Version 0.9.0 (2024-01-10)
- 🔧 Correction des tests
- 🔧 Amélioration de la sécurité
- 🔧 Optimisation des performances

### Version 0.8.0 (2024-01-05)
- ✨ Ajout des contrôleurs de base
- ✨ Connexion base de données
- ✨ Configuration initiale

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

*Documentation générée le 2024-01-15 pour le projet MSPR-TPRE-601-API*.