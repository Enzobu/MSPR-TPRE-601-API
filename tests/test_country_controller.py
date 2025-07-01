"""
Tests pour le module country_controller.py
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token


class TestCountryController:
    """Tests pour les routes du contrôleur de pays."""
    
    def test_get_all_countries_success(self, client, mock_db_connection):
        """Test de récupération de tous les pays."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_countries = [
            {'id_country': 1, 'name': 'France', 'iso_code': 'FR', 'population': 67000000, 'pib': '$2800000000000', 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1},
            {'id_country': 2, 'name': 'Germany', 'iso_code': 'DE', 'population': 83000000, 'pib': '$3800000000000', 'latitude': 51.1657, 'longitude': 10.4515, 'id_continent': 1, 'id_region': 2}
        ]
        
        with patch('controller.country_controller.execute_query', return_value=(mock_countries, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/api/countries', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['name'] == 'France'
        assert response.json[0]['pib'] == 2800000000000.0  # PIB nettoyé
    
    def test_get_all_countries_error(self, client):
        """Test de gestion d'erreur lors de la récupération des pays."""
        with patch('controller.country_controller.execute_query', return_value=(None, "Database error")):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/api/countries', headers=headers)
        
        assert response.status_code == 500
        assert 'Database error' in response.json['error']
    
    def test_get_country_by_id_success(self, client):
        """Test de récupération d'un pays par ID."""
        mock_country = {'id_country': 1, 'name': 'France', 'pib': '$2800000000000', 'iso_code': 'FR', 'population': 67000000, 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_country, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/api/country/1', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'France'
        assert response.json['pib'] == 2800000000000.0
    
    def test_get_country_by_id_not_found(self, client):
        """Test de récupération d'un pays inexistant."""
        with patch('controller.country_controller.execute_query', return_value=(None, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/api/country/999', headers=headers)
        
        assert response.status_code == 404
        assert 'not found' in response.json['error']
    
    def test_get_country_by_name_success(self, client):
        """Test de récupération d'un pays par nom."""
        mock_country = {'id_country': 1, 'name': 'France', 'pib': '$2800000000000', 'iso_code': 'FR', 'population': 67000000, 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_country, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/api/country/name/France', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'France'
    
    def test_create_country_success(self, client, sample_country_data):
        """Test de création d'un pays."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.post('/api/country', headers=headers, json=sample_country_data)
        
        assert response.status_code == 201
        assert response.json['id_country'] == 1
    
    def test_create_country_error(self, client, sample_country_data):
        """Test de gestion d'erreur lors de la création d'un pays."""
        with patch('controller.country_controller.execute_query', return_value=(None, "Database error")):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.post('/api/country', headers=headers, json=sample_country_data)
        
        assert response.status_code == 500
        assert 'Database error' in response.json['error']
    
    def test_update_country_success(self, client, sample_country_data):
        """Test de mise à jour d'un pays."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.put('/api/country/1', headers=headers, json=sample_country_data)
        
        assert response.status_code == 200
        assert 'updated successfully' in response.json['message']
    
    def test_update_country_not_found(self, client, sample_country_data):
        """Test de mise à jour d'un pays inexistant."""
        with patch('controller.country_controller.execute_query', return_value=(None, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.put('/api/country/999', headers=headers, json=sample_country_data)
        
        assert response.status_code == 404
        assert 'Country not found' in response.json['error']
    
    def test_delete_country_success(self, client):
        """Test de suppression d'un pays."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.delete('/api/country/1', headers=headers)
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message']
    
    def test_delete_country_not_found(self, client):
        """Test de suppression d'un pays inexistant."""
        with patch('controller.country_controller.execute_query', return_value=(None, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.delete('/api/country/999', headers=headers)
        
        assert response.status_code == 404
        assert 'Country not found' in response.json['error']


class TestCountryNamespace:
    """Tests pour les endpoints Swagger des pays."""
    
    def test_countries_namespace_get(self, client, mock_db_connection):
        """Test de l'endpoint GET /swagger/countries."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_countries = [
            {'id_country': 1, 'name': 'France', 'iso_code': 'FR', 'population': 67000000, 'pib': '$2800000000000', 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1},
            {'id_country': 2, 'name': 'Germany', 'iso_code': 'DE', 'population': 83000000, 'pib': '$3800000000000', 'latitude': 51.1657, 'longitude': 10.4515, 'id_continent': 1, 'id_region': 2}
        ]
        
        with patch('controller.country_controller.execute_query', return_value=(mock_countries, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/swagger/countries', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['name'] == 'France'
    
    def test_country_post_namespace(self, client, sample_country_data):
        """Test de l'endpoint POST /swagger/country."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.post('/swagger/country', headers=headers, json=sample_country_data)
        
        assert response.status_code == 201
        assert response.json['id_country'] == 1
    
    def test_country_by_id_namespace_get(self, client):
        """Test de l'endpoint GET /swagger/country/{id}."""
        mock_country = {'id_country': 1, 'name': 'France', 'iso_code': 'FR', 'population': 67000000, 'pib': '$2800000000000', 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_country, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/swagger/country/1', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'France'
    
    def test_country_by_id_namespace_put(self, client, sample_country_data):
        """Test de l'endpoint PUT /swagger/country/{id}."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.put('/swagger/country/1', headers=headers, json=sample_country_data)
        
        assert response.status_code == 200
        assert 'updated successfully' in response.json['message']
    
    def test_country_by_id_namespace_delete(self, client):
        """Test de l'endpoint DELETE /swagger/country/{id}."""
        mock_result = {'id_country': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_result, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.delete('/swagger/country/1', headers=headers)
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message']
    
    def test_country_by_name_namespace(self, client):
        """Test de l'endpoint GET /swagger/country/name/{name}."""
        mock_country = {'id_country': 1, 'name': 'France', 'iso_code': 'FR', 'population': 67000000, 'pib': '$2800000000000', 'latitude': 46.2276, 'longitude': 2.2137, 'id_continent': 1, 'id_region': 1}
        
        with patch('controller.country_controller.execute_query', return_value=(mock_country, None)):
            with client.application.app_context():
                token = create_access_token(identity='1')
                headers = {'Authorization': f'Bearer {token}'}
                
                response = client.get('/swagger/country/name/France', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'France'


class TestCountryUtilityFunctions:
    """Tests pour les fonctions utilitaires du contrôleur pays."""
    
    def test_clean_pib_value_string_with_dollar(self):
        """Test de nettoyage de la valeur PIB avec dollar."""
        from controller.country_controller import clean_pib_value
        
        result = clean_pib_value('$2,800,000,000,000')
        assert result == 2800000000000.0
    
    def test_clean_pib_value_string_without_dollar(self):
        """Test de nettoyage de la valeur PIB sans dollar."""
        from controller.country_controller import clean_pib_value
        
        result = clean_pib_value('2,800,000,000,000')
        assert result == 2800000000000.0
    
    def test_clean_pib_value_numeric(self):
        """Test de nettoyage de la valeur PIB déjà numérique."""
        from controller.country_controller import clean_pib_value
        
        result = clean_pib_value(2800000000000.0)
        assert result == 2800000000000.0
    
    def test_clean_pib_value_integer(self):
        """Test de nettoyage de la valeur PIB entière."""
        from controller.country_controller import clean_pib_value
        
        result = clean_pib_value(2800000000000)
        assert result == 2800000000000
    
    @patch('controller.country_controller.DBConnection')
    def test_execute_query_success_fetch_all(self, mock_db_class):
        """Test de la fonction execute_query avec fetch_all."""
        from controller.country_controller import execute_query
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_class.return_value.__enter__.return_value = mock_conn
        mock_db_class.return_value.__exit__.return_value = None
        
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'France'}]
        
        result, error = execute_query("SELECT * FROM country", fetch_all=True)
        
        assert error is None
        assert result == [{'id': 1, 'name': 'France'}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM country", None)
    
    @patch('controller.country_controller.DBConnection')
    def test_execute_query_success_fetch_one(self, mock_db_class):
        """Test de la fonction execute_query avec fetch_one."""
        from controller.country_controller import execute_query
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_class.return_value.__enter__.return_value = mock_conn
        mock_db_class.return_value.__exit__.return_value = None
        
        mock_cursor.fetchone.return_value = {'id': 1, 'name': 'France'}
        
        result, error = execute_query("SELECT * FROM country WHERE id = %s", (1,), fetch_one=True)
        
        assert error is None
        assert result == {'id': 1, 'name': 'France'}
        mock_cursor.execute.assert_called_once_with("SELECT * FROM country WHERE id = %s", (1,))
    
    @patch('controller.country_controller.DBConnection')
    def test_execute_query_error(self, mock_db_class):
        """Test de la fonction execute_query avec erreur."""
        from controller.country_controller import execute_query
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_class.return_value.__enter__.return_value = mock_conn
        mock_db_class.return_value.__exit__.return_value = None
        
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result, error = execute_query("SELECT * FROM country")
        
        assert result is None
        assert error == "Database error"
    
    @patch('controller.country_controller.DBConnection')
    def test_execute_query_no_fetch(self, mock_db_class):
        """Test de la fonction execute_query sans fetch."""
        from controller.country_controller import execute_query
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_class.return_value.__enter__.return_value = mock_conn
        mock_db_class.return_value.__exit__.return_value = None
        
        result, error = execute_query("INSERT INTO country VALUES (%s)", ('France',))
        
        assert error is None
        assert result is None
        mock_conn.commit.assert_called_once()


class TestCountryModel:
    """Tests pour le modèle Swagger des pays."""
    
    def test_country_model_structure(self, test_app):
        """Test de la structure du modèle pays."""
        from controller.country_controller import country_namespace
        
        country_model = country_namespace.models['Country']
        
        expected_fields = [
            'id_country', 'name', 'iso_code', 'population', 
            'pib', 'latitude', 'longitude', 'id_continent', 'id_region'
        ]
        
        for field in expected_fields:
            assert field in country_model
    
    def test_country_model_field_types(self, test_app):
        """Test des types de champs du modèle pays."""
        from controller.country_controller import country_namespace
        from flask_restx import fields
        
        country_model = country_namespace.models['Country']
        
        assert isinstance(country_model['id_country'], fields.Integer)
        assert isinstance(country_model['name'], fields.String)
        assert isinstance(country_model['iso_code'], fields.String)
        assert isinstance(country_model['population'], fields.Integer)
        assert isinstance(country_model['pib'], fields.Float)
        assert isinstance(country_model['latitude'], fields.Float)
        assert isinstance(country_model['longitude'], fields.Float) 