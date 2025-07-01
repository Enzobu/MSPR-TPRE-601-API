"""
Module de gestion des continents pour l'API.

Ce module définit des routes et des ressources pour gérer les continents dans une base de données via Flask.
Il permet de :

- Récupérer tous les continents.
- Récupérer un continent spécifique par ID ou par nom.
- Créer un nouveau continent.
- Mettre à jour un continent existant.
- Supprimer un continent.

Le module utilise Flask-RESTX pour la création des API RESTful et une connexion à la base de données
PostgreSQL pour interagir avec les données des continents.

Les routes sont organisées sous un blueprint Flask et un namespace Flask-RESTX pour une gestion claire et
modulaire des ressources de l'API.

Modules utilisés :
- Flask : Pour la gestion des routes et des vues.
- Flask-RESTX : Pour la gestion des API RESTful.
- psycopg2 : Pour la connexion et l'exécution de requêtes SQL sur une base de données PostgreSQL.
"""

from flask import Blueprint, request                # type: ignore
from flask_restx import Namespace, Resource, fields # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
import psycopg2.extras                              # type: ignore
from connect_db import DBConnection


continent_controller = Blueprint('continent_controller', __name__)

continent_namespace = Namespace('continent', description='Gestion des continents')

continent_model = continent_namespace.model('Continent', {
    'id_continent': fields.Integer(readonly=True, description='ID du continent'),
    'name': fields.String(required=True, description='Nom du continent')
})

def fetch_continents():
    """
    Récupère tous les continents de la base de données.

    :return: Liste des continents ou une liste vide en cas d'erreur.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM continent")
            continents = cursor.fetchall()
            return continents
    except Exception as e:
        print("Erreur lors de la récupération des données des continents:", e)
        return []

@continent_controller.route('/continents', methods=['GET'])
@jwt_required()
def get_continents():
    """
    Récupère tous les continents.

    :return: Liste des continents en JSON si trouvés, ou un message d'erreur si aucun continent n'est trouvé.
    """
    continents = fetch_continents()
    if not continents:
        return {"error": "No continents found"}, 404
    return continents, 200

@continent_controller.route('/continent/<int:continent_id>', methods=['GET'])
@jwt_required()
def get_continent_by_id(continent_id):
    """
    Récupère un continent spécifique par son ID.

    :param continent_id: ID du continent à récupérer.
    :return: Détails du continent en JSON si trouvé, ou un message d'erreur si le continent n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM continent WHERE id_continent = %s", (continent_id,))
            continent = cursor.fetchone()
            if not continent:
                return {"error": "Continent not found"}, 404
            return continent, 200
    except Exception as e:
        print("Erreur lors de la récupération des données du continent:", e)
        return {"error": "An error occurred"}, 500

@continent_controller.route('/continent/name/<string:continent_name>', methods=['GET'])
@jwt_required()
def get_continent_by_name(continent_name):
    """
    Récupère un continent spécifique par son nom.

    :param continent_name: Nom du continent à récupérer.
    :return: Détails du continent en JSON si trouvé, ou un message d'erreur si le continent n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM continent WHERE name = %s", (continent_name,))
            continent = cursor.fetchone()
            if not continent:
                return {"error": "Continent not found"}, 404
            return continent, 200
    except Exception as e:
        print("Erreur lors de la récupération des données du continent:", e)
        return {"error": "An error occurred"}, 500

@continent_controller.route('/continent', methods=['POST'])
@jwt_required()
def create_continent():
    """
    Crée un nouveau continent dans la base de données.

    :return: Détails du continent créé en JSON, ou un message d'erreur si la création échoue.
    """
    try:
        new_continent = request.json
        if "name" not in new_continent:
            return {"error": "Missing 'name'"}, 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO continent (name) VALUES (%s) RETURNING id_continent",
                (new_continent["name"],)
            )
            new_continent_id = cursor.fetchone()[0]
            conn.commit()

        return {
            "id_continent": new_continent_id,
            "name": new_continent["name"]
        }, 201

    except Exception as e:
        print("Erreur lors de la création du continent:", e)
        return {"error": "An error occurred"}, 500

@continent_controller.route('/continent/<int:continent_id>', methods=['PUT'])
@jwt_required()
def update_continent(continent_id):
    """
    Met à jour un continent spécifique par son ID.

    :param continent_id: ID du continent à mettre à jour.
    :return: Détails du continent mis à jour en JSON, ou un message d'erreur si le continent n'est pas trouvé.
    """
    try:
        updated_continent = request.json
        if "name" not in updated_continent:
            return {"error": "Missing 'name'"}, 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE continent
                SET name = %s
                WHERE id_continent = %s
                RETURNING id_continent, name
                """,
                (updated_continent["name"], continent_id)
            )
            updated_data = cursor.fetchone()
            if not updated_data:
                return {"error": "Continent not found"}, 404

            conn.commit()

        return {
            "id_continent": updated_data[0],
            "name": updated_data[1]
        }, 200

    except Exception as e:
        print("Erreur lors de la mise à jour du continent:", e)
        return {"error": "An error occurred"}, 500

@continent_controller.route('/continent/<int:continent_id>', methods=['DELETE'])
@jwt_required()
def delete_continent(continent_id):
    """
    Supprime un continent spécifique par son ID.

    :param continent_id: ID du continent à supprimer.
    :return: Message de succès de suppression ou un message d'erreur si le continent n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM continent WHERE id_continent = %s RETURNING id_continent",
                (continent_id,)
            )
            deleted_data = cursor.fetchone()

            if not deleted_data:
                return {"error": "Continent not found"}, 404

            conn.commit()

        return {"message": f"Continent with ID {continent_id} has been deleted successfully"}, 200

    except Exception as e:
        print("Erreur lors de la suppression du continent:", e)
        return {"error": "An error occurred"}, 500

@continent_namespace.route('/continents')
class Continents(Resource):
    """
    Classe API pour récupérer tous les continents.
    """
    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Récupère tous les continents.")
    @continent_namespace.marshal_list_with(continent_model)
    def get(self):
        """
        Récupère la liste de tous les continents.

        :return: Une liste de continents en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = get_continents()
        if status_code != 200:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

@continent_namespace.route('/continent')
class ContinentPost(Resource):
    """
    Classe API pour créer un nouveau continent.
    """
    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Crée un nouveau continent.")
    @continent_namespace.expect(continent_model)
    def post(self):
        """
        Crée un nouveau continent avec les données fournies.

        :return: Détails du continent créé en JSON avec un code de statut 201 si la création réussit,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = create_continent()
        if status_code != 201:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

@continent_namespace.route('/continent/<int:continent_id>')
class ContinentById(Resource):
    """
    Classe API pour récupérer, mettre à jour et supprimer un continent par son ID.
    """
    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Récupère un continent par ID.")
    @continent_namespace.marshal_with(continent_model)
    def get(self, continent_id):
        """
        Récupère un continent spécifique à partir de son ID.

        :param continent_id: L'ID du continent à récupérer.
        :return: Les détails du continent en JSON avec un code de statut 200 si trouvé,
                 ou une erreur avec un code de statut 404 si non trouvé.
        """
        response, status_code = get_continent_by_id(continent_id)
        if status_code != 200:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Met à jour un continent existant.")
    @continent_namespace.expect(continent_model)
    def put(self, continent_id):
        """
        Met à jour un continent spécifique à partir de son ID.

        :param continent_id: L'ID du continent à mettre à jour.
        :return: Les détails du continent mis à jour en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si le continent n'existe pas.
        """
        response, status_code = update_continent(continent_id)
        if status_code != 200:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Supprime un continent par ID.")
    def delete(self, continent_id):
        """
        Supprime un continent spécifique à partir de son ID.

        :param continent_id: L'ID du continent à supprimer.
        :return: Un message de confirmation en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si le continent n'existe pas.
        """
        response, status_code = delete_continent(continent_id)
        if status_code != 200:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

@continent_namespace.route('/continent/name/<string:continent_name>')
class ContinentByName(Resource):
    """
    Classe API pour récupérer un continent par son nom.
    """
    @jwt_required()
    @continent_namespace.doc(security='Bearer', description="Récupère un continent par nom.")
    @continent_namespace.marshal_with(continent_model)
    def get(self, continent_name):
        """
        Récupère un continent spécifique à partir de son nom.

        :param continent_name: Le nom du continent à récupérer.
        :return: Les détails du continent en JSON avec un code de statut 200 si trouvé,
                 ou une erreur avec un code de statut 404 si non trouvé.
        """
        response, status_code = get_continent_by_name(continent_name)
        if status_code != 200:
            continent_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code
