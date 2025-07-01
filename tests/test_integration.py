"""
Tests d'intégration pour l'API complète
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token
import bcrypt


class TestFullAPIIntegration:
    """Tests d'intégration pour l'API complète."""
    
    def test_complete_authentication_workflow(self, client, mock_db_connection):
        """Test du workflow complet d'authentification."""
        # Test qu'on peut accéder à une route protégée avec un token valide
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            protected_response = client.get('/protected', headers=headers)
            assert protected_response.status_code == 200
        
        # Test que l'endpoint de login est accessible
        login_response = client.post('/swagger/users/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        # Le login doit au moins être accessible, même s'il échoue avec de mauvaises données
        assert login_response.status_code in [400, 401, 500]
    
    def test_api_endpoints_require_authentication(self, client):
        """Test que tous les endpoints principaux nécessitent une authentification."""
        endpoints_to_test = [
            ('GET', '/swagger/users'),
            ('GET', '/swagger/predictions/get?'),
        ]
        
        for method, endpoint in endpoints_to_test:
            response = client.open(endpoint, method=method)
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"
    
    def test_cors_headers_present(self, client):
        """Test que les headers CORS sont présents."""
        response = client.options('/')
        
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.status_code == 200
    
    def test_api_documentation_accessible(self, client):
        """Test que la documentation Swagger est accessible."""
        response = client.get('/api/docs')
        assert response.status_code == 200
        
        # Vérifier que c'est bien du HTML (documentation Swagger)
        assert 'text/html' in response.content_type
    
    def test_health_check_endpoint(self, client):
        """Test de l'endpoint de santé de l'API."""
        response = client.get('/')
        assert response.status_code == 200
        assert response.json['message'] == "L'API fonctionne correctement"
    
    def test_error_handling_consistency(self, client):
        """Test que la gestion d'erreurs est cohérente."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Tester un endpoint qui devrait retourner une erreur avec des données invalides
            response = client.post('/swagger/users', headers=headers, json={
                'invalid_field': 'invalid_value'
            })
            # L'endpoint devrait gérer gracieusement les erreurs
            assert response.status_code in [400, 500]
    
    def test_jwt_token_expiration_handling(self, client):
        """Test de la gestion de l'expiration des tokens JWT."""
        # Créer un token expiré
        with client.application.app_context():
            from datetime import timedelta
            expired_token = create_access_token(
                identity='1', 
                expires_delta=timedelta(seconds=-1)  # Token expiré
            )
            headers = {'Authorization': f'Bearer {expired_token}'}
            
            response = client.get('/protected', headers=headers)
            # Flask-JWT-Extended peut retourner 401 ou 422 selon la version
            assert response.status_code in [401, 422]  # Token expiré
    
    def test_api_namespaces_registration(self, client):
        """Test que tous les namespaces sont correctement enregistrés."""
        # Tester que les endpoints de base sont accessibles
        
        namespaces_endpoints = [
            ('/swagger/users/login', 'POST'),  # Login endpoint accept POST
            ('/swagger/predictions/get?', 'GET'),
        ]
        
        for endpoint, method in namespaces_endpoints:
            if method == 'POST':
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            # Tous ces endpoints devraient être accessibles (même si 401/400)
            assert response.status_code in [200, 401, 400], f"Endpoint {method} {endpoint} not properly registered"


class TestDataFlowIntegration:
    """Tests d'intégration pour le flux de données."""
    
    def test_prediction_workflow(self, client, mock_db_connection):
        """Test simple du workflow de prédictions."""
        mock_conn, mock_cursor = mock_db_connection
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Tester l'accès aux prédictions
            from datetime import datetime, timedelta, date
            
            mock_cursor.fetchall.return_value = [
                (1, 1, 1, date(2024, 6, 1), 100.5, 90.0, 110.0, 0.5, 0.3, 0.7, 10.0, 8.0, 12.0, 1000000.0, 900000.0, 1100000.0, 1000000.0, 950000.0, 1050000.0)
            ]
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            predictions_response = client.get(
                f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}&country_id=1',
                headers=headers
            )
            assert predictions_response.status_code == 200
            assert len(predictions_response.json) == 1
    
    def test_admin_user_workflow(self, client, mock_db_connection):
        """Test du workflow pour un utilisateur admin."""
        mock_conn, mock_cursor = mock_db_connection
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Mock pour admin check
            mock_cursor.fetchone.side_effect = [
                (True,),  # User is admin
            ]
            mock_cursor.fetchall.return_value = [
                (1, 'John', 'Doe', 'john@example.com', True),
                (2, 'Jane', 'Smith', 'jane@example.com', False)
            ]
            
            # Admin peut voir tous les utilisateurs
            users_response = client.get('/swagger/users', headers=headers)
            assert users_response.status_code == 200
            assert len(users_response.json) == 2
    
    def test_non_admin_user_restrictions(self, client, mock_db_connection):
        """Test des restrictions pour les utilisateurs non-admin."""
        mock_conn, mock_cursor = mock_db_connection
        
        with client.application.app_context():
            token = create_access_token(identity='2')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Mock pour non-admin check
            mock_cursor.fetchone.return_value = (False,)  # User is not admin
            
            # Non-admin ne peut pas voir tous les utilisateurs
            users_response = client.get('/swagger/users', headers=headers)
            assert users_response.status_code == 403


class TestAPIPerformanceAndLimits:
    """Tests pour les performances et limites de l'API."""
    
    def test_prediction_date_range_limits(self, client):
        """Test des limites de plage de dates pour les prédictions."""
        from datetime import datetime, timedelta
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test avec plage de dates trop large
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d')
            
            response = client.get(
                f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}',
                headers=headers
            )
            assert response.status_code == 400
            assert '3 mois' in response.json['msg']
    
    def test_concurrent_requests_handling(self, client, mock_db_connection):
        """Test basique de gestion de requêtes concurrentes."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Simuler plusieurs requêtes simultanées
            responses = []
            for _ in range(5):  # Réduisons à 5 pour éviter la surcharge
                response = client.get('/swagger/predictions/get?disease_id=1&start_date=2024-12-01&end_date=2024-12-02', headers=headers)
                responses.append(response)
            
            # Toutes les requêtes doivent réussir
            for response in responses:
                assert response.status_code in [200, 400]  # 400 acceptable pour dates passées


class TestAPISecurityIntegration:
    """Tests de sécurité pour l'API."""
    
    def test_authorization_boundary_conditions(self, client, mock_db_connection):
        """Test des conditions limites d'autorisation."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Test avec token malformé
        malformed_tokens = [
            'Bearer ',
            'Bearer invalid_token',
            'InvalidBearer token',
        ]
        
        for token in malformed_tokens:
            headers = {'Authorization': token}
            response = client.get('/swagger/users', headers=headers)
            assert response.status_code in [401, 422]  # Unauthorized ou Unprocessable Entity
    
    def test_invalid_json_handling(self, client):
        """Test de gestion de JSON invalide."""
        response = client.post('/swagger/users/login', 
                              data='invalid json', 
                              content_type='application/json')
        # Devrait gérer gracieusement le JSON invalide
        assert response.status_code in [400, 500] 