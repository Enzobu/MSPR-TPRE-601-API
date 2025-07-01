"""
Tests pour le module prediction_controller.py
"""

import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta, date


class TestPredictionResource:
    """Tests pour la ressource de prédictions."""
    
    def test_get_predictions_success(self, client, mock_db_connection):
        """Test de récupération des prédictions avec succès."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Données de test simulant la base de données
        mock_predictions = [
            (1, 1, 1, date(2024, 6, 1), 100.5, 90.0, 110.0, 0.5, 0.3, 0.7, 10.0, 8.0, 12.0, 1000000.0, 900000.0, 1100000.0, 1000000.0, 950000.0, 1050000.0),
            (2, 1, 1, date(2024, 6, 2), 101.0, 91.0, 111.0, 0.6, 0.4, 0.8, 11.0, 9.0, 13.0, 1010000.0, 910000.0, 1110000.0, 1010000.0, 960000.0, 1060000.0)
        ]
        mock_cursor.fetchall.return_value = mock_predictions
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Calculer les dates futures pour le test (au moins 1 jour dans le futur)
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['yhat'] == 100.5
        assert response.json[0]['ds'] == '2024-06-01'
    
    def test_get_predictions_with_country_filter(self, client, mock_db_connection):
        """Test de récupération des prédictions avec filtre par pays."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_predictions = [
            (1, 2, 1, date(2024, 6, 1), 100.5, 90.0, 110.0, 0.5, 0.3, 0.7, 10.0, 8.0, 12.0, 1000000.0, 900000.0, 1100000.0, 1000000.0, 950000.0, 1050000.0)
        ]
        mock_cursor.fetchall.return_value = mock_predictions
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}&country_id=2', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['id_country'] == 2
    
    def test_get_predictions_missing_parameters(self, client):
        """Test de récupération des prédictions avec paramètres manquants."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/predictions/get?', headers=headers)
        
        assert response.status_code == 400
        assert 'Paramètres requis : disease_id, start_date, end_date' in response.json['msg']
    
    def test_get_predictions_missing_disease_id(self, client):
        """Test de récupération des prédictions sans disease_id."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 400
        assert 'Paramètres requis : disease_id, start_date, end_date' in response.json['msg']
    
    def test_get_predictions_missing_start_date(self, client):
        """Test de récupération des prédictions sans start_date."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&end_date={end_date}', headers=headers)
        
        assert response.status_code == 400
        assert 'Paramètres requis : disease_id, start_date, end_date' in response.json['msg']
    
    def test_get_predictions_missing_end_date(self, client):
        """Test de récupération des prédictions sans end_date."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}', headers=headers)
        
        assert response.status_code == 400
        assert 'Paramètres requis : disease_id, start_date, end_date' in response.json['msg']
    
    def test_get_predictions_invalid_date_format(self, client):
        """Test de récupération des prédictions avec format de date invalide."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/swagger/predictions/get?disease_id=1&start_date=invalid-date&end_date=2024-06-30', headers=headers)
        
        assert response.status_code == 400
        assert 'Les dates doivent être au format YYYY-MM-DD' in response.json['msg']
    

    
    def test_get_predictions_start_date_today(self, client, mock_db_connection):
        """Test de récupération des prédictions avec date de début aujourd'hui (devrait réussir)."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            today_date = datetime.now().strftime('%Y-%m-%d')
            future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={today_date}&end_date={future_date}', headers=headers)
        
        # La date d'aujourd'hui est acceptée selon l'implémentation (start_date < today)
        assert response.status_code == 200
    
    def test_get_predictions_end_date_too_far(self, client):
        """Test de récupération des prédictions avec date de fin trop éloignée."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=91)).strftime('%Y-%m-%d')  # Plus de 90 jours
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 400
        assert 'La date de fin ne peut pas dépasser 3 mois à partir d\'aujourd\'hui' in response.json['msg']
    
    def test_get_predictions_unauthorized(self, client):
        """Test de récupération des prédictions sans authentification."""
        start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}')
        
        assert response.status_code == 401
    
    def test_get_predictions_database_error(self, client, mock_db_connection):
        """Test de gestion d'erreur de base de données."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Database connection failed")
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 500
        assert 'Erreur serveur' in response.json['msg']
    
    def test_get_predictions_empty_result(self, client, mock_db_connection):
        """Test de récupération des prédictions avec résultat vide."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) == 0
    
    def test_get_predictions_sql_query_structure(self, client, mock_db_connection):
        """Test de la structure de la requête SQL."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}&country_id=2', headers=headers)
        
        # Vérifier que la requête SQL contient les éléments attendus
        called_args = mock_cursor.execute.call_args
        query = called_args[0][0]
        params = called_args[0][1]
        
        assert 'SELECT' in query
        assert 'FROM prediction' in query
        assert 'WHERE id_disease = %s' in query
        assert 'AND ds BETWEEN %s AND %s' in query
        assert 'AND id_country = %s' in query
        assert 'ORDER BY ds ASC, id_country ASC, id_prediction ASC' in query
        
        # Vérifier les paramètres
        assert len(params) == 4  # disease_id, start_date, end_date, country_id
        assert params[0] == '1'  # disease_id
        assert params[3] == '2'  # country_id


class TestPredictionDateValidation:
    """Tests spécifiques pour la validation des dates."""
    
    def test_date_validation_exactly_90_days(self, client, mock_db_connection):
        """Test avec exactement 90 jours de différence."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')  # Exactement 90 jours
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 200  # Devrait passer
    
    def test_date_validation_91_days(self, client):
        """Test avec 91 jours de différence (devrait échouer)."""
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=91)).strftime('%Y-%m-%d')  # Plus de 90 jours
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 400
        assert 'La date de fin ne peut pas dépasser 3 mois à partir d\'aujourd\'hui' in response.json['msg']


class TestPredictionModel:
    """Tests pour le modèle Swagger des prédictions."""
    
    def test_prediction_model_structure(self, test_app):
        """Test de la structure du modèle prédiction."""
        from controller.prediction_controller import prediction_namespace
        
        prediction_model = prediction_namespace.models['Prediction']
        
        expected_fields = [
            'id_prediction', 'id_country', 'id_disease', 'ds',
            'yhat', 'yhat_lower', 'yhat_upper',
            'trend', 'trend_lower', 'trend_upper',
            'deaths', 'deaths_lower', 'deaths_upper',
            'pib', 'pib_lower', 'pib_upper',
            'population', 'population_lower', 'population_upper'
        ]
        
        for field in expected_fields:
            assert field in prediction_model
    
    def test_prediction_model_field_types(self, test_app):
        """Test des types de champs du modèle prédiction."""
        from controller.prediction_controller import prediction_namespace
        
        prediction_model = prediction_namespace.models['Prediction']
        
        # Vérifier que les champs principaux existent dans le modèle
        assert 'id_prediction' in prediction_model
        assert 'id_country' in prediction_model
        assert 'id_disease' in prediction_model
        assert 'ds' in prediction_model
        assert 'yhat' in prediction_model
        assert 'trend' in prediction_model
        assert 'deaths' in prediction_model
        assert 'pib' in prediction_model
        assert 'population' in prediction_model
        
        # Vérifier que le modèle a le bon nombre de champs
        expected_field_count = 19  # Nombre total de champs dans le modèle
        assert len(prediction_model) == expected_field_count


class TestPredictionDataProcessing:
    """Tests pour le traitement des données de prédiction."""
    
    def test_date_formatting_in_response(self, client, mock_db_connection):
        """Test du formatage des dates dans la réponse."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Date de test avec un objet date Python
        test_date = date(2024, 12, 25)
        mock_predictions = [
            (1, 1, 1, test_date, 100.5, 90.0, 110.0, 0.5, 0.3, 0.7, 10.0, 8.0, 12.0, 1000000.0, 900000.0, 1100000.0, 1000000.0, 950000.0, 1050000.0)
        ]
        mock_cursor.fetchall.return_value = mock_predictions
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        assert response.status_code == 200
        assert response.json[0]['ds'] == '2024-12-25'
    
    def test_numeric_values_in_response(self, client, mock_db_connection):
        """Test des valeurs numériques dans la réponse."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_predictions = [
            (1, 1, 1, date(2024, 6, 1), 100.5, 90.0, 110.0, 0.5, 0.3, 0.7, 10.0, 8.0, 12.0, 1000000.0, 900000.0, 1100000.0, 1000000.0, 950000.0, 1050000.0)
        ]
        mock_cursor.fetchall.return_value = mock_predictions
        
        with client.application.app_context():
            token = create_access_token(identity='1')
            headers = {'Authorization': f'Bearer {token}'}
            
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = client.get(f'/swagger/predictions/get?disease_id=1&start_date={start_date}&end_date={end_date}', headers=headers)
        
        prediction = response.json[0]
        
        # Vérifier tous les champs numériques
        assert prediction['yhat'] == 100.5
        assert prediction['yhat_lower'] == 90.0
        assert prediction['yhat_upper'] == 110.0
        assert prediction['trend'] == 0.5
        assert prediction['trend_lower'] == 0.3
        assert prediction['trend_upper'] == 0.7
        assert prediction['deaths'] == 10.0
        assert prediction['deaths_lower'] == 8.0
        assert prediction['deaths_upper'] == 12.0
        assert prediction['pib'] == 1000000.0
        assert prediction['pib_lower'] == 900000.0
        assert prediction['pib_upper'] == 1100000.0
        assert prediction['population'] == 1000000.0
        assert prediction['population_lower'] == 950000.0
        assert prediction['population_upper'] == 1050000.0 