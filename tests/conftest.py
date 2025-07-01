"""
Configuration pytest et fixtures communes pour tous les tests.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import importlib.util

# Mock psycopg2 avant tout import
mock_psycopg2 = MagicMock()
mock_psycopg2.extras = MagicMock()
mock_psycopg2.connect = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = mock_psycopg2.extras

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import corrigé pour l'application Flask
app_file_path = os.path.join(os.path.dirname(__file__), '..', 'app.py')
if not os.path.exists(app_file_path):
    # Si on est dans le container, le chemin est différent
    app_file_path = '/app/app.py'

spec = importlib.util.spec_from_file_location("app_module", app_file_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app_module
spec.loader.exec_module(app_module)


@pytest.fixture(scope='session')
def test_app():
    """Fixture pour l'application Flask de test."""
    app_instance = app_module.app
    app_instance.config['TESTING'] = True
    app_instance.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app_instance.config['WTF_CSRF_ENABLED'] = False
    return app_instance


@pytest.fixture(scope='function')
def client(test_app):
    """Fixture pour le client de test Flask."""
    with test_app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def mock_db_connection():
    """Fixture pour mocker la connexion à la base de données."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Mock pour la classe DBConnection qui utilise le gestionnaire de contexte
    mock_db_instance = MagicMock()
    mock_db_instance.__enter__ = MagicMock(return_value=mock_connection)
    mock_db_instance.__exit__ = MagicMock(return_value=None)
    
    with patch('connect_db.DBConnection', return_value=mock_db_instance), \
         patch('controller.login_controller.DBConnection', return_value=mock_db_instance), \
         patch('controller.prediction_controller.DBConnection', return_value=mock_db_instance), \
         patch('controller.country_controller.DBConnection', return_value=mock_db_instance), \
         patch('controller.disease_controller.DBConnection', return_value=mock_db_instance), \
         patch('controller.continent_controller.DBConnection', return_value=mock_db_instance), \
         patch('controller.region_controller.DBConnection', return_value=mock_db_instance):
        yield mock_connection, mock_cursor


@pytest.fixture(scope='function')
def auth_headers(test_app):
    """Fixture pour les headers d'authentification JWT."""
    with test_app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity='1')
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def sample_user_data():
    """Fixture pour les données d'utilisateur de test."""
    return {
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'password123',
        'isAdmin': False
    }


@pytest.fixture(scope='function')
def sample_country_data():
    """Fixture pour les données de pays de test."""
    return {
        'name': 'France',
        'iso_code': 'FR',
        'population': 67000000,
        'pib': 2800000000000.0,
        'latitude': 46.2276,
        'longitude': 2.2137,
        'id_continent': 1,
        'id_region': 1
    }


@pytest.fixture(scope='function')
def sample_disease_data():
    """Fixture pour les données de maladie de test."""
    return {
        'name': 'COVID-19',
        'is_pandemic': True
    }


@pytest.fixture(scope='function')
def sample_prediction_data():
    """Fixture pour les données de prédiction de test."""
    from datetime import date
    return {
        'id_prediction': 1,
        'id_country': 1,
        'id_disease': 1,
        'ds': date(2024, 6, 1),
        'yhat': 100.5,
        'yhat_lower': 90.0,
        'yhat_upper': 110.0,
        'trend': 0.5,
        'trend_lower': 0.3,
        'trend_upper': 0.7,
        'deaths': 10.0,
        'deaths_lower': 8.0,
        'deaths_upper': 12.0,
        'pib': 1000000.0,
        'pib_lower': 900000.0,
        'pib_upper': 1100000.0,
        'population': 1000000.0,
        'population_lower': 950000.0,
        'population_upper': 1050000.0
    }


@pytest.fixture(autouse=True)
def clean_db_patches():
    """Nettoie les patches après chaque test."""
    yield
    # Cleanup automatique des patches 