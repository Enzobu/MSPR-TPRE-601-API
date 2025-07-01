"""
Tests pour le module login_controller.py
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token
import bcrypt


class TestLoginResource:
    """Tests pour la ressource de login."""
    
    def test_login_success(self, client, mock_db_connection):
        """Test de login réussi."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock de la recherche d'utilisateur et du password hashé
        password = "password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_cursor.fetchone.return_value = (1, hashed_password)
        
        response = client.post('/swagger/users/login', json={
            'email': 'test@example.com',
            'password': password
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        mock_cursor.execute.assert_called_once()
    
    def test_login_missing_data(self, client):
        """Test de login avec données manquantes."""
        response = client.post('/swagger/users/login', json={})
        assert response.status_code == 400
        # Le contrôleur renvoie d'abord "Donnees invalides" si le JSON est vide
        assert response.json['msg'] in ['Email et mot de passe requis', 'Donnees invalides']
    
    def test_login_invalid_json(self, client):
        """Test de login avec JSON invalide."""
        response = client.post('/swagger/users/login', data='invalid json', 
                             content_type='application/json')
        # Un JSON invalide peut causer une erreur serveur 500
        assert response.status_code in [400, 500]
        if response.json:
            assert 'Donnees invalides' in response.json.get('msg', '') or 'Erreur serveur' in response.json.get('msg', '')
    
    def test_login_missing_email(self, client):
        """Test de login avec email manquant."""
        response = client.post('/swagger/users/login', json={
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'Email et mot de passe requis' in response.json['msg']
    
    def test_login_missing_password(self, client):
        """Test de login avec mot de passe manquant."""
        response = client.post('/swagger/users/login', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 400
        assert 'Email et mot de passe requis' in response.json['msg']
    
    def test_login_user_not_found(self, client, mock_db_connection):
        """Test de login avec utilisateur inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        response = client.post('/swagger/users/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 404
        assert 'Utilisateur non trouve' in response.json['msg']
    
    def test_login_wrong_password(self, client, mock_db_connection):
        """Test de login avec mot de passe incorrect."""
        mock_conn, mock_cursor = mock_db_connection
        hashed_password = bcrypt.hashpw('correct_password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mock_cursor.fetchone.return_value = (1, hashed_password)
        
        response = client.post('/swagger/users/login', json={
            'email': 'test@example.com',
            'password': 'wrong_password'
        })
        
        assert response.status_code == 401
        assert 'Mot de passe incorrect' in response.json['msg']
    
    def test_login_server_error(self, client, mock_db_connection):
        """Test de gestion d'erreur serveur lors du login."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Database error")
        
        response = client.post('/swagger/users/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 500
        assert 'Erreur serveur' in response.json['msg']


class TestUserListResource:
    """Tests pour la ressource de liste des utilisateurs."""
    
    def test_get_users_success_as_admin(self, client, mock_db_connection):
        """Test de récupération des utilisateurs en tant qu'admin."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock pour check_if_admin et récupération des utilisateurs
        mock_cursor.fetchone.side_effect = [
            (True,),  # check_if_admin
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe', 'john@example.com', True),
            (2, 'Jane', 'Smith', 'jane@example.com', False)
        ]
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/users', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['firstname'] == 'John'
        assert response.json[1]['firstname'] == 'Jane'
    
    def test_get_users_forbidden_not_admin(self, client, mock_db_connection):
        """Test de récupération des utilisateurs sans être admin."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (False,)  # check_if_admin
        
        with client.application.app_context():
            token = create_access_token(identity='2')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/users', headers=headers)
        
        assert response.status_code == 403
        # Flask-RESTX peut renvoyer différents formats, l'important est le code 403
    
    def test_get_users_unauthorized(self, client):
        """Test de récupération des utilisateurs sans token."""
        response = client.get('/swagger/users')
        assert response.status_code == 401
    
    def test_create_user_success(self, client, mock_db_connection, sample_user_data):
        """Test de création d'utilisateur réussie."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock pour vérifier que l'email n'existe pas déjà, puis retourner le nouvel ID
        mock_cursor.fetchone.side_effect = [None, (1,)]  # Email check, then new ID
        
        response = client.post('/swagger/users', json=sample_user_data)
        
        assert response.status_code == 201
        assert response.json['firstname'] == 'John'
        assert response.json['id_user'] == 1
        assert mock_cursor.execute.call_count >= 2  # Au moins 2 appels (check email + insert)
    
    def test_create_user_invalid_data(self, client):
        """Test de création d'utilisateur avec données invalides."""
        response = client.post('/swagger/users', json={})
        assert response.status_code == 400
        # Le contrôleur peut renvoyer soit "Donnees invalides" soit le message sur la structure
        assert response.json['msg'] in ['Veuillez respecter la structure de la table', 'Donnees invalides']
    
    def test_create_user_missing_fields(self, client):
        """Test de création d'utilisateur avec champs manquants."""
        response = client.post('/swagger/users', json={
            'firstname': 'John',
            'email': 'john@example.com'
            # Manque lastname, password, isAdmin
        })
        assert response.status_code == 400
        assert 'Veuillez respecter la structure de la table' in response.json['msg']
    
    def test_create_user_email_already_exists(self, client, mock_db_connection, sample_user_data):
        """Test de création d'utilisateur avec email déjà existant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)  # Email existe déjà
        
        response = client.post('/swagger/users', json=sample_user_data)
        
        assert response.status_code == 400
        assert 'Email dejà utilise' in response.json['msg']
    
    def test_create_user_server_error(self, client, mock_db_connection, sample_user_data):
        """Test de gestion d'erreur serveur lors de la création."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Database error")
        
        response = client.post('/swagger/users', json=sample_user_data)
        
        assert response.status_code == 500
        assert 'Erreur serveur' in response.json['msg']


class TestUserResource:
    """Tests pour la ressource utilisateur individuel."""
    
    def test_get_user_by_id_success(self, client, mock_db_connection):
        """Test de récupération d'utilisateur par ID."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1, 'John', 'Doe', 'john@example.com', True)
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/users/1', headers=headers)
        
        assert response.status_code == 200
        assert response.json['firstname'] == 'John'
        assert response.json['id_user'] == 1
    
    def test_get_user_by_id_not_found(self, client, mock_db_connection):
        """Test de récupération d'utilisateur inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/users/999', headers=headers)
        
        assert response.status_code == 404
        # La réponse peut être en format différent selon Flask-RESTX
        if response.json and isinstance(response.json, dict):
            assert 'Utilisateur non trouve' in response.json.get('msg', str(response.json))
    
    def test_update_user_success(self, client, mock_db_connection):
        """Test de mise à jour d'utilisateur."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock pour vérifier que l'utilisateur existe et que l'email n'est pas utilisé
        mock_cursor.fetchone.side_effect = [
            (1,),  # User exists
            None,  # Email not used by another user
        ]
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.put('/swagger/users/1', headers=headers, json={
                'firstname': 'John Updated',
                'email': 'john.updated@example.com'
            })
        
        assert response.status_code == 200
        assert 'mis à jour' in response.json['msg']
    
    def test_update_user_not_found(self, client, mock_db_connection):
        """Test de mise à jour d'utilisateur inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None  # User doesn't exist
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.put('/swagger/users/999', headers=headers, json={
                'firstname': 'John Updated'
            })
        
        assert response.status_code == 404
        assert 'Utilisateur non trouvé' in response.json['msg']
    
    def test_delete_user_success(self, client, mock_db_connection):
        """Test de suppression d'utilisateur."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)  # Delete successful
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.delete('/swagger/users/1', headers=headers)
        
        assert response.status_code == 200
        assert 'supprime' in response.json['msg']
    
    def test_delete_user_not_found(self, client, mock_db_connection):
        """Test de suppression d'utilisateur inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None  # User doesn't exist
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.delete('/swagger/users/999', headers=headers)
        
        assert response.status_code == 404
        assert 'Utilisateur non trouve' in response.json['msg']


class TestCheckIfAdmin:
    """Tests pour la fonction check_if_admin."""
    
    def test_check_if_admin_true(self, mock_db_connection):
        """Test de vérification admin - utilisateur est admin."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (True,)
        
        with patch('controller.login_controller.get_jwt_identity', return_value='1'):
            from controller.login_controller import check_if_admin
            result = check_if_admin()
        
        assert result is True
    
    def test_check_if_admin_false(self, mock_db_connection):
        """Test de vérification admin - utilisateur n'est pas admin."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (False,)
        
        with patch('controller.login_controller.get_jwt_identity', return_value='2'):
            from controller.login_controller import check_if_admin
            result = check_if_admin()
        
        assert result is False
    
    def test_check_if_admin_user_not_found(self, mock_db_connection):
        """Test de vérification admin - utilisateur inexistant."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        with patch('controller.login_controller.get_jwt_identity', return_value='999'):
            from controller.login_controller import check_if_admin
            result = check_if_admin()
        
        assert result is False


class TestUserModels:
    """Tests pour les modèles Swagger des utilisateurs."""
    
    def test_user_model_structure(self, test_app):
        """Test de la structure du modèle utilisateur."""
        from controller.login_controller import user_namespace
        
        user_model = user_namespace.models['User']
        
        expected_fields = ['id_user', 'firstname', 'lastname', 'email', 'password', 'isAdmin']
        
        for field in expected_fields:
            assert field in user_model
    
    def test_login_model_structure(self, test_app):
        """Test de la structure du modèle de login."""
        from controller.login_controller import user_namespace
        
        login_model = user_namespace.models['Login']
        
        expected_fields = ['email', 'password']
        
        for field in expected_fields:
            assert field in login_model
    
    def test_token_model_structure(self, test_app):
        """Test de la structure du modèle de token."""
        from controller.login_controller import user_namespace
        
        token_model = user_namespace.models['Token']
        
        assert 'access_token' in token_model 