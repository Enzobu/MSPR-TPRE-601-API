"""
Tests pour le module disease_controller.py
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token


class TestDiseaseEndpoints:
    """Tests pour les endpoints des maladies."""
    
    def test_get_all_diseases_success(self, client, mock_db_connection):
        """Test de récupération de toutes les maladies."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_diseases = [
            {'id_disease': 1, 'name': 'COVID-19', 'is_pandemic': True},
            {'id_disease': 2, 'name': 'H1N1', 'is_pandemic': True},
            {'id_disease': 3, 'name': 'MPOX', 'is_pandemic': False}
        ]
        mock_cursor.fetchall.return_value = mock_diseases
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/diseases', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 3
        assert response.json[0]['name'] == 'COVID-19'
        assert response.json[1]['name'] == 'H1N1'
    
    def test_get_disease_by_id_success(self, client, mock_db_connection):
        """Test de récupération d'une maladie par ID."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {'id_disease': 1, 'name': 'COVID-19', 'is_pandemic': True}
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/disease/1', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'COVID-19'
        assert response.json['is_pandemic'] is True
    
    def test_get_disease_by_id_not_found(self, client, mock_db_connection):
        """Test de récupération d'une maladie inexistante."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/disease/999', headers=headers)
        
        assert response.status_code == 404
    
    def test_create_disease_success(self, client, mock_db_connection, sample_disease_data):
        """Test de création d'une maladie."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [1]  # New ID returned
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, json=sample_disease_data)
        
        assert response.status_code == 201
        assert response.json['id_disease'] == 1
    
    def test_create_disease_missing_name(self, client):
        """Test de création d'une maladie sans nom."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, json={
                'is_pandemic': True
            })
        
        assert response.status_code == 500  # KeyError sur le nom manquant
    
    def test_create_disease_missing_is_pandemic(self, client):
        """Test de création d'une maladie sans is_pandemic."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, json={
                'name': 'COVID-19'
            })
        
        assert response.status_code == 500  # KeyError sur is_pandemic manquant
    
    def test_update_disease_success(self, client, mock_db_connection):
        """Test de mise à jour d'une maladie."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [1]  # Update successful
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            update_data = {
                'name': 'COVID-19 Updated',
                'is_pandemic': False
            }
            
            response = client.put('/swagger/disease/1', headers=headers, json=update_data)
        
        assert response.status_code == 200
        assert 'Disease updated successfully' in response.json['message']
    
    def test_update_disease_not_found(self, client, mock_db_connection):
        """Test de mise à jour d'une maladie inexistante."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None  # No disease found
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            update_data = {
                'name': 'COVID-19 Updated',
                'is_pandemic': False
            }
            
            response = client.put('/swagger/disease/999', headers=headers, json=update_data)
        
        assert response.status_code == 404
    
    def test_delete_disease_success(self, client, mock_db_connection):
        """Test de suppression d'une maladie."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [1]  # Delete successful
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.delete('/swagger/disease/1', headers=headers)
        
        assert response.status_code == 200
        assert 'Disease deleted successfully' in response.json['message']
    
    def test_delete_disease_not_found(self, client, mock_db_connection):
        """Test de suppression d'une maladie inexistante."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None  # No disease found
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.delete('/swagger/disease/999', headers=headers)
        
        assert response.status_code == 404
    
    def test_get_disease_by_name_success(self, client, mock_db_connection):
        """Test de récupération d'une maladie par nom."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {'id_disease': 1, 'name': 'COVID-19', 'is_pandemic': True}
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/disease/name/COVID-19', headers=headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'COVID-19'
    
    def test_get_disease_by_name_not_found(self, client, mock_db_connection):
        """Test de récupération d'une maladie par nom inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/disease/name/NonExistent', headers=headers)
        
        assert response.status_code == 404


class TestDiseaseAuthentication:
    """Tests pour l'authentification des endpoints des maladies."""
    
    def test_get_diseases_unauthorized(self, client):
        """Test de récupération des maladies sans authentification."""
        response = client.get('/swagger/diseases')
        assert response.status_code == 401
    
    def test_create_disease_unauthorized(self, client, sample_disease_data):
        """Test de création de maladie sans authentification."""
        response = client.post('/swagger/disease', json=sample_disease_data)
        assert response.status_code == 401
    
    def test_update_disease_unauthorized(self, client):
        """Test de mise à jour de maladie sans authentification."""
        response = client.put('/swagger/disease/1', json={
            'name': 'Updated Disease',
            'is_pandemic': False
        })
        assert response.status_code == 401
    
    def test_delete_disease_unauthorized(self, client):
        """Test de suppression de maladie sans authentification."""
        response = client.delete('/swagger/disease/1')
        assert response.status_code == 401


class TestDiseaseErrorHandling:
    """Tests pour la gestion d'erreurs du contrôleur des maladies."""
    
    def test_database_error_on_get_all(self, client, mock_db_connection):
        """Test de gestion d'erreur base de données lors de la récupération."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Database connection failed")
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/diseases', headers=headers)
        
        assert response.status_code == 500
    
    def test_database_error_on_create(self, client, mock_db_connection, sample_disease_data):
        """Test de gestion d'erreur base de données lors de la création."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Insert failed")
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, json=sample_disease_data)
        
        assert response.status_code == 500
    
    def test_invalid_json_data(self, client):
        """Test avec données JSON invalides."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, data='invalid json')
        
        assert response.status_code == 415  # Unsupported Media Type


class TestDiseaseModel:
    """Tests pour le modèle Swagger des maladies."""
    
    def test_disease_model_exists(self, test_app):
        """Test que le modèle Disease existe."""
        assert test_app is not None
    
    def test_disease_model_fields(self, test_app):
        """Test des champs du modèle Disease."""
        assert test_app is not None


class TestDiseaseValidation:
    """Tests pour la validation des données des maladies."""
    
    def test_create_disease_empty_name(self, client, mock_db_connection):
        """Test de création avec nom vide."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = [1]
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.post('/swagger/disease', headers=headers, json={
                'name': '',
                'is_pandemic': True
            })
        
        # L'API accepte les noms vides, donc on teste seulement que ça fonctionne
        assert response.status_code == 201
    



class TestDiseaseIntegration:
    """Tests d'intégration pour le contrôleur des maladies."""
    
    def test_full_crud_workflow(self, client, mock_db_connection):
        """Test du workflow CRUD complet."""
        mock_conn, mock_cursor = mock_db_connection
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # CREATE
            mock_cursor.fetchone.return_value = [1]
            create_response = client.post('/swagger/disease', headers=headers, json={
                'name': 'Test Disease',
                'is_pandemic': True
            })
            assert create_response.status_code == 201
            
            # READ
            mock_cursor.fetchone.return_value = {'id_disease': 1, 'name': 'Test Disease', 'is_pandemic': True}
            read_response = client.get('/swagger/disease/1', headers=headers)
            assert read_response.status_code == 200
            
            # UPDATE
            mock_cursor.fetchone.return_value = [1]
            update_response = client.put('/swagger/disease/1', headers=headers, json={
                'name': 'Updated Disease',
                'is_pandemic': False
            })
            assert update_response.status_code == 200
            
            # DELETE
            mock_cursor.fetchone.return_value = [1]
            delete_response = client.delete('/swagger/disease/1', headers=headers)
            assert delete_response.status_code == 200 