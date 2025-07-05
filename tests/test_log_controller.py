"""
Tests pour le module log_controller.py
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token
from datetime import date, datetime
from decimal import Decimal


class TestLogControllerModels:
    """Tests pour les modèles Swagger du contrôleur de logs."""
    
    def test_metrics_response_model_structure(self, test_app):
        """Test de la structure du modèle de réponse des métriques."""
        from controller.log_controller import log_namespace
        
        metrics_model = log_namespace.models['MetricsResponse']
        
        expected_fields = ['id_metrics', '_date', 'is_sucess', 'error_string', 'id_country']
        
        for field in expected_fields:
            assert field in metrics_model
    
    def test_error_model_structure(self, test_app):
        """Test de la structure du modèle d'erreur."""
        from controller.log_controller import log_namespace
        
        error_model = log_namespace.models['ErrorResponse']
        
        assert 'error' in error_model


class TestMetricsByCountryResource:
    """Tests pour la ressource de récupération des métriques par pays."""
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_by_country_success(self, mock_get_db, client):
        """Test de récupération des logs pour un pays spécifique."""
        # Mock de la connexion et du curseur
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        # Mock des données de log
        mock_cursor.fetchone.return_value = (
            1,  # id_log
            date(2024, 6, 30),  # _date
            True,  # is_success
            None,  # error_string
            4,  # id_country
            'France',  # name
            'FR',  # iso_code
            Decimal('68000000'),  # population
            Decimal('3200000000'),  # pib
            Decimal('48.8'),  # latitude
            Decimal('2.3'),  # longitude
            1,  # id_continent
            3   # id_region
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
        
        assert response.status_code == 200
        assert response.json['id_log'] == 1
        assert response.json['_date'] == '2024-06-30'
        assert response.json['is_success'] is True
        assert response.json['country']['name'] == 'France'
        assert response.json['country']['iso_code'] == 'FR'
        assert response.json['country']['population'] == 68000000.0
        # Vérifier que la connexion a été fermée
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_by_country_not_found(self, mock_get_db, client):
        """Test de récupération des logs pour un pays inexistant."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = None
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=999', headers=headers)
        
        assert response.status_code == 400
        assert 'Aucune métrique trouvée pour le pays donné' in response.json['error']
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_all_logs_success(self, mock_get_db, client):
        """Test de récupération de tous les logs."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        # Mock des données de logs multiples
        mock_cursor.fetchall.return_value = [
            (
                1, date(2024, 6, 30), True, None, 4, 'France', 'FR',
                Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3
            ),
            (
                2, date(2024, 6, 29), False, 'Erreur de connexion', 5, 'Germany', 'DE',
                Decimal('83000000'), Decimal('4000000000'), Decimal('51.5'), Decimal('10.5'), 1, 2
            )
        ]
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id_log'] == 1
        assert response.json[0]['country']['name'] == 'France'
        assert response.json[1]['id_log'] == 2
        assert response.json[1]['country']['name'] == 'Germany'
        assert response.json[1]['is_success'] is False
        assert response.json[1]['error_string'] == 'Erreur de connexion'
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_all_logs_empty_result(self, mock_get_db, client):
        """Test de récupération de tous les logs quand aucun résultat."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get', headers=headers)
        
        assert response.status_code == 400
        assert 'Aucune métrique trouvée pour le pays donné' in response.json['error']
        mock_conn.close.assert_called_once()
    
    def test_get_logs_unauthorized(self, client):
        """Test de récupération des logs sans token d'authentification."""
        response = client.get('/swagger/logs/get')
        assert response.status_code == 401
    
    def test_get_logs_invalid_token(self, client):
        """Test de récupération des logs avec token invalide."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/swagger/logs/get', headers=headers)
        assert response.status_code == 422
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_server_error(self, mock_get_db, client):
        """Test de gestion d'erreur serveur lors de la récupération des logs."""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        # Simuler une erreur lors de l'exécution
        mock_conn.cursor.side_effect = Exception("Database connection error")
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
        
        assert response.status_code == 500
        assert 'Database connection error' in response.json['error']
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_with_decimal_conversion(self, mock_get_db, client):
        """Test de conversion des valeurs Decimal en float."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        # Mock avec des valeurs Decimal
        mock_cursor.fetchone.return_value = (
            1, date(2024, 6, 30), True, None, 4, 'France', 'FR',
            Decimal('68000000.50'), Decimal('3200000000.75'), 
            Decimal('48.856'), Decimal('2.3522'), 1, 3
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
        
        assert response.status_code == 200
        # Vérifier que les valeurs Decimal sont converties en float
        assert isinstance(response.json['country']['population'], float)
        assert isinstance(response.json['country']['pib'], float)
        assert isinstance(response.json['country']['latitude'], float)
        assert isinstance(response.json['country']['longitude'], float)
        assert response.json['country']['population'] == 68000000.50
        assert response.json['country']['pib'] == 3200000000.75
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_with_error_string(self, mock_get_db, client):
        """Test de récupération des logs avec message d'erreur."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = (
            1, date(2024, 6, 30), False, 'Erreur de traitement des données', 4, 'France', 'FR',
            Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
        
        assert response.status_code == 200
        assert response.json['is_success'] is False
        assert response.json['error_string'] == 'Erreur de traitement des données'
        mock_conn.close.assert_called_once()
    
    @patch('controller.log_controller.get_db_connection')
    def test_get_logs_date_formatting(self, mock_get_db, client):
        """Test du formatage des dates dans la réponse."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        test_date = date(2024, 12, 25)
        mock_cursor.fetchone.return_value = (
            1, test_date, True, None, 4, 'France', 'FR',
            Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
        
        assert response.status_code == 200
        assert response.json['_date'] == '2024-12-25'
        mock_conn.close.assert_called_once()


class TestLogControllerIntegration:
    """Tests d'intégration pour le contrôleur de logs."""
    
    @patch('controller.log_controller.get_db_connection')
    def test_full_log_retrieval_workflow(self, mock_get_db, client):
        """Test du workflow complet de récupération des logs."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        # Test 1: Récupération par pays
        mock_cursor.fetchone.return_value = (
            1, date(2024, 6, 30), True, None, 4, 'France', 'FR',
            Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Récupération par pays
            response1 = client.get('/swagger/logs/get?id_country=4', headers=headers)
            assert response1.status_code == 200
            assert response1.json['country']['name'] == 'France'
            
            # Test 2: Récupération de tous les logs
            mock_cursor.fetchall.return_value = [
                (1, date(2024, 6, 30), True, None, 4, 'France', 'FR',
                 Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3),
                (2, date(2024, 6, 29), False, 'Erreur', 5, 'Germany', 'DE',
                 Decimal('83000000'), Decimal('4000000000'), Decimal('51.5'), Decimal('10.5'), 1, 2)
            ]
            
            response2 = client.get('/swagger/logs/get', headers=headers)
            assert response2.status_code == 200
            assert len(response2.json) == 2
            
        # Vérifier que la connexion a été fermée
        assert mock_conn.close.call_count >= 2
    
    @patch('controller.log_controller.get_db_connection')
    def test_error_handling_consistency(self, mock_get_db, client):
        """Test de cohérence dans la gestion des erreurs."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test avec pays inexistant
            mock_cursor.fetchone.return_value = None
            response1 = client.get('/swagger/logs/get?id_country=999', headers=headers)
            assert response1.status_code == 400
            assert 'error' in response1.json
            
            # Test avec aucun log disponible
            mock_cursor.fetchall.return_value = []
            response2 = client.get('/swagger/logs/get', headers=headers)
            assert response2.status_code == 400
            assert 'error' in response2.json
            
        # Vérifier que la connexion a été fermée
        assert mock_conn.close.call_count >= 2
    
    @patch('controller.log_controller.get_db_connection')
    def test_database_connection_cleanup(self, mock_get_db, client):
        """Test que la connexion à la base de données est bien fermée."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_db.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = (
            1, date(2024, 6, 30), True, None, 4, 'France', 'FR',
            Decimal('68000000'), Decimal('3200000000'), Decimal('48.8'), Decimal('2.3'), 1, 3
        )
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/logs/get?id_country=4', headers=headers)
            assert response.status_code == 200
            
            # Vérifier que la connexion a été fermée
            mock_conn.close.assert_called_once() 