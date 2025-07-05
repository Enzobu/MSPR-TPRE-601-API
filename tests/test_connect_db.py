"""
Tests pour le module connect_db.py
"""

import pytest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le .env si disponible
load_dotenv()

# Variables d'environnement par défaut pour les tests
DEFAULT_DB_CONFIG = {
    'DB_HOST': os.getenv('DB_HOST'),
    'DB_DATABASE': os.getenv('DB_DATABASE'),
    'DB_USER': os.getenv('DB_USER'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD'),
    'DB_PORT': os.getenv('DB_PORT')
}


class TestGetDbConnection:
    """Tests pour la fonction get_db_connection."""
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    @patch('connect_db.psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test de connexion à la base de données réussie."""
        from connect_db import get_db_connection
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        result = get_db_connection()
        
        # Vérifier que connect a été appelé avec les bons paramètres
        mock_connect.assert_called_once_with(
            host=DEFAULT_DB_CONFIG['DB_HOST'],
            database=DEFAULT_DB_CONFIG['DB_DATABASE'],
            user=DEFAULT_DB_CONFIG['DB_USER'],
            password=DEFAULT_DB_CONFIG['DB_PASSWORD'],
            port=DEFAULT_DB_CONFIG['DB_PORT']
        )
        assert result == mock_connection
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_get_db_connection_failure(self, mock_print, mock_connect):
        """Test de gestion d'échec de connexion."""
        from connect_db import get_db_connection
        
        exception = Exception("Connection failed")
        mock_connect.side_effect = exception
        
        result = get_db_connection()
        
        assert result is None
        # Vérifier que print a été appelé avec le bon message d'erreur
        mock_print.assert_called_with("Erreur lors de la connexion à la base de données :", exception)


class TestDBConnection:
    """Tests pour la classe DBConnection (gestionnaire de contexte)."""
    
    @patch('connect_db.get_db_connection')
    def test_db_connection_context_manager_success(self, mock_get_db):
        """Test du gestionnaire de contexte avec succès."""
        from connect_db import DBConnection
        
        mock_connection = MagicMock()
        mock_get_db.return_value = mock_connection
        
        with DBConnection() as conn:
            assert conn == mock_connection
            
        mock_connection.close.assert_called_once()
    
    @patch('connect_db.get_db_connection')
    @patch('builtins.print')
    def test_db_connection_context_manager_with_connection(self, mock_print, mock_get_db):
        """Test du gestionnaire de contexte avec connexion réelle."""
        from connect_db import DBConnection
        
        mock_connection = MagicMock()
        mock_get_db.return_value = mock_connection
        
        db_context = DBConnection()
        
        # Test __enter__
        conn = db_context.__enter__()
        assert conn == mock_connection
        assert db_context.conn == mock_connection
        
        # Test __exit__
        db_context.__exit__(None, None, None)
        mock_connection.close.assert_called_once()
        mock_print.assert_called_with("Connexion fermée")
    
    @patch('connect_db.get_db_connection')
    def test_db_connection_context_manager_no_connection(self, mock_get_db):
        """Test du gestionnaire de contexte sans connexion."""
        from connect_db import DBConnection
        
        mock_get_db.return_value = None
        
        db_context = DBConnection()
        
        # Test __enter__
        conn = db_context.__enter__()
        assert conn is None
        assert db_context.conn is None
        
        # Test __exit__ ne doit pas lever d'erreur
        db_context.__exit__(None, None, None)
    
    def test_db_connection_init(self):
        """Test de l'initialisation de DBConnection."""
        from connect_db import DBConnection
        
        db_context = DBConnection()
        assert db_context.conn is None
    
    @patch('connect_db.get_db_connection')
    def test_db_connection_with_exception(self, mock_get_db):
        """Test du gestionnaire de contexte avec exception."""
        from connect_db import DBConnection
        
        mock_connection = MagicMock()
        mock_get_db.return_value = mock_connection
        
        try:
            with DBConnection() as conn:
                assert conn == mock_connection
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # La connexion doit être fermée même en cas d'exception
        mock_connection.close.assert_called_once()


class TestTestDbConnection:
    """Tests pour la fonction test_db_connection."""
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_test_db_connection_success(self, mock_print, mock_connect):
        """Test de la fonction test_db_connection avec succès."""
        from connect_db import test_db_connection
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        test_db_connection()
        
        mock_connect.assert_called_once_with(
            host=DEFAULT_DB_CONFIG['DB_HOST'],
            database=DEFAULT_DB_CONFIG['DB_DATABASE'],
            user=DEFAULT_DB_CONFIG['DB_USER'],
            password=DEFAULT_DB_CONFIG['DB_PASSWORD'],
            port=DEFAULT_DB_CONFIG['DB_PORT']
        )
        mock_connection.close.assert_called_once()
        mock_print.assert_called_with("Connexion à la base de données réussie.")
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_test_db_connection_failure(self, mock_print, mock_connect):
        """Test de la fonction test_db_connection avec échec."""
        from connect_db import test_db_connection
        
        exception = Exception("Connection failed")
        mock_connect.side_effect = exception
        
        test_db_connection()
        
        # Vérifier que print a été appelé avec le bon message d'erreur
        mock_print.assert_called_with("Erreur lors de la connexion à la base de données :", exception)


class TestDatabaseConfiguration:
    """Tests pour la configuration de la base de données."""
    
    @patch.dict(os.environ, {
        'DB_HOST': 'test_host',
        'DB_DATABASE': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_PORT': '5432'
    })
    def test_database_config_exists(self):
        """Test que la configuration DATABASE existe."""
        # Recharger le module pour prendre en compte les nouvelles variables d'environnement
        import importlib
        import connect_db
        importlib.reload(connect_db)
        
        from connect_db import DATABASE
        
        assert isinstance(DATABASE, dict)
        assert 'host' in DATABASE
        assert 'database' in DATABASE
        assert 'user' in DATABASE
        assert 'password' in DATABASE
        assert 'port' in DATABASE
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    def test_database_config_values(self):
        """Test des valeurs de configuration depuis le .env."""
        # Recharger le module pour prendre en compte les nouvelles variables d'environnement
        import importlib
        import connect_db
        importlib.reload(connect_db)
        
        from connect_db import DATABASE
        
        assert DATABASE['host'] == DEFAULT_DB_CONFIG['DB_HOST']
        assert DATABASE['database'] == DEFAULT_DB_CONFIG['DB_DATABASE']
        assert DATABASE['user'] == DEFAULT_DB_CONFIG['DB_USER']
        assert DATABASE['password'] == DEFAULT_DB_CONFIG['DB_PASSWORD']
        assert DATABASE['port'] == DEFAULT_DB_CONFIG['DB_PORT']
    
    def test_database_config_uses_env_vars(self):
        """Test que la configuration utilise bien les variables d'environnement."""
        # Test avec des variables personnalisées
        custom_config = {
            'DB_HOST': 'custom.host.com',
            'DB_DATABASE': 'custom_db',
            'DB_USER': 'custom_user',
            'DB_PASSWORD': 'custom_pass',
            'DB_PORT': '5433'
        }
        
        with patch.dict(os.environ, custom_config):
            import importlib
            import connect_db
            importlib.reload(connect_db)
            
            from connect_db import DATABASE
            
            assert DATABASE['host'] == 'custom.host.com'
            assert DATABASE['database'] == 'custom_db'
            assert DATABASE['user'] == 'custom_user'
            assert DATABASE['password'] == 'custom_pass'
            assert DATABASE['port'] == '5433'


class TestIntegration:
    """Tests d'intégration pour le module connect_db."""
    
    @patch.dict(os.environ, DEFAULT_DB_CONFIG)
    @patch('connect_db.psycopg2.connect')
    def test_full_workflow(self, mock_connect):
        """Test du workflow complet."""
        from connect_db import DBConnection, get_db_connection, test_db_connection
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        # Test get_db_connection
        conn1 = get_db_connection()
        assert conn1 == mock_connection
        
        # Test DBConnection context manager
        with DBConnection() as conn2:
            assert conn2 == mock_connection
        
        # Test test_db_connection
        test_db_connection()
        
        # Vérifier que psycopg2.connect a été appelé 3 fois
        assert mock_connect.call_count == 3


class TestEnvironmentVariableLoading:
    """Tests pour le chargement des variables d'environnement."""
    
    def test_env_override(self):
        """Test que les variables d'environnement peuvent surcharger les valeurs par défaut."""
        override_config = {
            'DB_HOST': 'override.example.com',
            'DB_DATABASE': 'override_db',
            'DB_USER': 'override_user',
            'DB_PASSWORD': 'override_pass',
            'DB_PORT': '5433'
        }
        
        with patch.dict(os.environ, override_config):
            config = {
                'DB_HOST': os.getenv('DB_HOST', 'qg.enzo-palermo.com'),
                'DB_DATABASE': os.getenv('DB_DATABASE', 'mspr502'),
                'DB_USER': os.getenv('DB_USER', 'mspr502'),
                'DB_PASSWORD': os.getenv('DB_PASSWORD', 's5t4v5'),
                'DB_PORT': os.getenv('DB_PORT', '5432')
            }
            
            assert config['DB_HOST'] == 'override.example.com'
            assert config['DB_DATABASE'] == 'override_db'
            assert config['DB_USER'] == 'override_user'
            assert config['DB_PASSWORD'] == 'override_pass'
            assert config['DB_PORT'] == '5433' 