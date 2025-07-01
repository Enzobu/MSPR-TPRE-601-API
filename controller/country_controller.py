"""
Module de gestion des pays via une API Flask.

Ce module définit plusieurs routes pour créer, récupérer, mettre à jour et supprimer des pays
dans une base de données PostgreSQL.
"""

from flask import Blueprint, request                    # type: ignore
from flask_restx import Namespace, Resource, fields     # type: ignore
from flask_jwt_extended import jwt_required             # type: ignore
import psycopg2.extras                                  # type: ignore
from connect_db import DBConnection


country_controller = Blueprint('country_controller', __name__)

country_namespace = Namespace('country', description='Gestion des pays')

country_model = country_namespace.model('Country', {
    'id_country': fields.Integer(readonly=True, description='ID du pays'),
    'name': fields.String(required=True, description='Nom du pays'),
    'iso_code': fields.String(required=True, description='Iso code du pays'),  # Changement: iso_code devient un String
    'population': fields.Integer(required=True, description='Population du pays'),
    'pib': fields.Float(description='PIB du pays'),
    'latitude': fields.Float(description='Latitude du pays'),  # Nouveau champ: latitude
    'longitude': fields.Float(description='Longitude du pays'),  # Nouveau champ: longitude
    'id_continent': fields.Integer(required=True, description='ID du continent'),
    'id_region': fields.Integer(description='ID de la région du pays')  # Nouveau champ: id_region
})

def clean_pib_value(pib_value):
    """
    Nettoie et convertit une valeur PIB sous forme de chaîne en float.
    
    :param pib_value: Valeur du PIB sous forme de chaîne ou de nombre.
    :return: Valeur du PIB sous forme de float.
    """
    if isinstance(pib_value, str):
        return float(pib_value.replace('$', '').replace(',', ''))
    return pib_value

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Exécute une requête SQL sur la base de données.
    
    :param query: Requête SQL à exécuter.
    :param params: Paramètres de la requête SQL.
    :param fetch_one: Indique si une seule ligne doit être récupérée.
    :param fetch_all: Indique si toutes les lignes doivent être récupérées.
    :return: Résultat de la requête et éventuelle erreur.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
            conn.commit()
            return result, None
    except Exception as e:
        return None, str(e)

@country_controller.route('/countries', methods=['GET'])
@jwt_required()
def get_all_countries():
    """
    Récupère la liste de tous les pays enregistrés dans la base de données.
    
    :return: Liste des pays et code HTTP.
    """
    query = "SELECT * FROM country"
    countries, error = execute_query(query, fetch_all=True)
    if error:
        return {"error": error}, 500
    for country in countries:
        country['pib'] = clean_pib_value(country.get('pib'))
    return countries, 200

@country_controller.route('/country/<int:country_id>', methods=['GET'])
@jwt_required()
def get_country_by_id(country_id):
    """
    Récupère un pays par son identifiant unique.
    
    :param country_id: Identifiant du pays.
    :return: Détails du pays et code HTTP.
    """
    query = "SELECT * FROM country WHERE id_country = %s"
    country, error = execute_query(query, (country_id,), fetch_one=True)
    if error:
        return {"error": error}, 500
    if country:
        country['pib'] = clean_pib_value(country.get('pib'))
        return country, 200
    return {"error": f"Country with ID {country_id} not found"}, 404

@country_controller.route('/country/name/<string:country_name>', methods=['GET'])
@jwt_required()
def get_country_by_name(country_name):
    """
    Récupère un pays par son nom.
    
    :param country_name: Nom du pays.
    :return: Détails du pays et code HTTP.
    """
    query = "SELECT * FROM country WHERE name = %s"
    country, error = execute_query(query, (country_name,), fetch_one=True)
    if error:
        return {"error": error}, 500
    if country:
        country['pib'] = clean_pib_value(country.get('pib'))
        return country, 200
    return {"error": f"Country with name {country_name} not found"}, 404

@country_controller.route('/country', methods=['POST'])
@jwt_required()
def create_country():
    """
    Crée un nouveau pays dans la base de données.
    
    :return: Identifiant du pays créé et code HTTP.
    """
    data = request.json

    query = """
        INSERT INTO country (name, iso_code, population, pib, latitude, longitude, id_continent, id_region)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_country
    """
    new_id, error = execute_query(query, (
        data['name'],
        data['iso_code'],  # Passer iso_code comme String
        data['population'],
        data.get('pib'),
        data.get('latitude'),  # Passer latitude
        data.get('longitude'),  # Passer longitude
        data['id_continent'],
        data.get('id_region')  # Passer id_region si disponible
    ), fetch_one=True)
    if error:
        return {"error": error}, 500
    return {"id_country": new_id['id_country']}, 201

@country_controller.route('/country/<int:country_id>', methods=['PUT'])
@jwt_required()
def update_country(country_id):
    """
    Met à jour les informations d'un pays existant.
    
    :param country_id: Identifiant du pays à mettre à jour.
    :return: Message de confirmation ou d'erreur et code HTTP.
    """
    data = request.json

    query = """
        UPDATE country
        SET name = %s, iso_code = %s, population = %s, pib = %s, latitude = %s, longitude = %s, id_continent = %s, id_region = %s
        WHERE id_country = %s
        RETURNING id_country
    """
    updated, error = execute_query(query, (
        data['name'],
        data['iso_code'],
        data['population'],
        data.get('pib'),
        data.get('latitude'),
        data.get('longitude'),
        data['id_continent'],
        data.get('id_region'),
        country_id
    ), fetch_one=True)
    if error:
        return {"error": error}, 500
    if updated:
        return {"message": "Country updated successfully"}, 200
    return {"error": "Country not found"}, 404

@country_controller.route('/country/<int:country_id>', methods=['DELETE'])
@jwt_required()
def delete_country(country_id):
    """
    Supprime un pays de la base de données.
    
    :param country_id: Identifiant du pays à supprimer.
    :return: Message de confirmation ou d'erreur et code HTTP.
    """
    query = "DELETE FROM country WHERE id_country = %s RETURNING id_country"
    deleted, error = execute_query(query, (country_id,), fetch_one=True)
    if error:
        return {"error": error}, 500
    if deleted:
        return {"message": "Country deleted successfully"}, 200
    return {"error": "Country not found"}, 404

@country_namespace.route('/countries')
class Countries(Resource):
    """
    Gestion des opérations liées aux pays.
    Cette classe permet de récupérer la liste de tous les pays.
    """
    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Récupère tous les pays.")
    @country_namespace.marshal_list_with(country_model)
    def get(self):
        """
        Récupère la liste de tous les pays.

        :return: Une liste des pays en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = get_all_countries()
        if status_code != 200:
            return {"error": response.get("error", "Erreur inconnue")}, status_code
        return response, status_code

@country_namespace.route('/country')
class CountryPost(Resource):
    """
    Création d'un nouveau pays.
    Cette classe gère la création d'un pays avec les informations requises.
    """
    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Crée un nouveau pays.")
    @country_namespace.expect(country_model)
    def post(self):
        """
        Crée un nouveau pays.

        :return: Les détails du pays créé en JSON avec un code de statut 201 si réussi,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = create_country()
        if status_code != 201:
            return {"error": response.get("error", "Invalid id_climat_type provided.")}, status_code
        return response, status_code

@country_namespace.route('/country/<int:country_id>')
class CountryById(Resource):
    """
    Gestion d'un pays par son identifiant.
    Cette classe permet de récupérer, mettre à jour et supprimer un pays spécifique.
    """
    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Récupère un pays par ID.")
    @country_namespace.marshal_with(country_model)
    def get(self, country_id):
        """
        Récupère un pays spécifique à partir de son ID.

        :param country_id: L'ID du pays à récupérer.
        :return: Les détails du pays en JSON avec un code de statut 200 si trouvé,
                 ou une erreur avec un code de statut 404 si non trouvé.
        """
        response, status_code = get_country_by_id(country_id)
        if status_code != 200:
            return {"error": response.get("error", "Erreur inconnue")}, status_code
        return response, status_code

    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Met à jour un pays existant.")
    @country_namespace.expect(country_model)
    def put(self, country_id):
        """
        Met à jour un pays spécifique à partir de son ID.

        :param country_id: L'ID du pays à mettre à jour.
        :return: Les détails du pays mis à jour en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si le pays n'existe pas.
        """
        response, status_code = update_country(country_id)
        if status_code != 200:
            return {"error": response.get("error", "Erreur inconnue")}, status_code
        return response, status_code

    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Supprime un pays par ID.")
    def delete(self, country_id):
        """
        Supprime un pays spécifique à partir de son ID.

        :param country_id: L'ID du pays à supprimer.
        :return: Un message de confirmation en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si le pays n'existe pas.
        """
        response, status_code = delete_country(country_id)
        if status_code != 200:
            return {"error": response.get("error", "Erreur inconnue")}, status_code
        return response, status_code

@country_namespace.route('/country/name/<string:country_name>')
class CountryByName(Resource):
    """
    Récupération d'un pays par son nom.
    Cette classe permet de récupérer un pays en utilisant son nom comme critère de recherche.
    """
    @jwt_required()
    @country_namespace.doc(security='Bearer', description="Récupère un pays par nom.")
    @country_namespace.marshal_with(country_model)
    def get(self, country_name):
        """
        Récupère un pays spécifique à partir de son nom.

        :param country_name: Le nom du pays à récupérer.
        :return: Les détails du pays en JSON avec un code de statut 200 si trouvé,
                 ou une erreur avec un code de statut 404 si non trouvé.
        """
        response, status_code = get_country_by_name(country_name)
        if status_code != 200:
            return {"error": response.get("error", "Erreur inconnue")}, status_code
        return response, status_code
