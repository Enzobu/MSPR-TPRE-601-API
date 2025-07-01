"""
Tests pour le module connect_db.py
"""

import pytest
from unittest.mock import patch, MagicMock
import psycopg2


class TestGetDbConnection:
    """Tests pour la fonction get_db_connection."""
    
    @patch('connect_db.psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test de connexion à la base de données réussie."""
        from connect_db import get_db_connection
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        result = get_db_connection()
        
        mock_connect.assert_called_once_with(
            host="qg.enzo-palermo.com",
            database="mspr502",
            user="mspr502",
            password="s5t4v5",
            port=5432
        )
        assert result == mock_connection
    
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_get_db_connection_failure(self, mock_print, mock_connect):
        """Test de gestion d'échec de connexion."""
        from connect_db import get_db_connection
        
        exception = Exception("Connection failed")
        mock_connect.side_effect = exception
        
        result = get_db_connection()
        
        assert result is None
        # Vérifier que print a été appelé avec le bon message d'erreur et une exception
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        assert call_args[0] == "Erreur lors de la connexion à la base de données :"
        assert isinstance(call_args[1], Exception)
        assert str(call_args[1]) == "Connection failed"


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
    
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_test_db_connection_success(self, mock_print, mock_connect):
        """Test de la fonction test_db_connection avec succès."""
        from connect_db import test_db_connection
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        test_db_connection()
        
        mock_connect.assert_called_once_with(
            host="qg.enzo-palermo.com",
            database="mspr502",
            user="mspr502",
            password="s5t4v5",
            port=5432
        )
        mock_connection.close.assert_called_once()
        mock_print.assert_called_with("Connexion à la base de données réussie.")
    
    @patch('connect_db.psycopg2.connect')
    @patch('builtins.print')
    def test_test_db_connection_failure(self, mock_print, mock_connect):
        """Test de la fonction test_db_connection avec échec."""
        from connect_db import test_db_connection
        
        exception = Exception("Connection failed")
        mock_connect.side_effect = exception
        
        test_db_connection()
        
        # Vérifier que print a été appelé avec le bon message d'erreur et une exception
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        assert call_args[0] == "Erreur lors de la connexion à la base de données :"
        assert isinstance(call_args[1], Exception)
        assert "Connection failed" in str(call_args[1])


class TestDatabaseConfiguration:
    """Tests pour la configuration de la base de données."""
    
    def test_database_config_exists(self):
        """Test que la configuration DATABASE existe."""
        from connect_db import DATABASE
        
        assert isinstance(DATABASE, dict)
        assert 'host' in DATABASE
        assert 'database' in DATABASE
        assert 'user' in DATABASE
        assert 'password' in DATABASE
        assert 'port' in DATABASE
    
    def test_database_config_values(self):
        """Test des valeurs de configuration."""
        from connect_db import DATABASE
        
        assert DATABASE['host'] == "qg.enzo-palermo.com"
        assert DATABASE['database'] == "mspr502"
        assert DATABASE['user'] == "mspr502"
        assert DATABASE['password'] == "s5t4v5"
        assert DATABASE['port'] == 5432


class TestIntegration:
    """Tests d'intégration pour le module connect_db."""
    
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