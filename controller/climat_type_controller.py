"""
Module de gestion des types de climat pour l'API.

Ce module définit des routes et des ressources pour gérer les types de climat dans une base de données via
Flask. Il permet de :

- Récupérer tous les types de climat.
- Récupérer un type de climat spécifique par ID ou par nom.
- Créer un nouveau type de climat.
- Mettre à jour un type de climat existant.
- Supprimer un type de climat.

Le module utilise Flask-RESTX pour créer des API RESTful et une connexion à la base de données PostgreSQL pour
interagir avec les données des types de climat.

Les routes sont organisées sous un blueprint Flask et un namespace Flask-RESTX pour une gestion claire et
modulaire des ressources de l'API.

Modules utilisés :
- Flask : Pour la gestion des routes et des vues.
- Flask-RESTX : Pour la gestion des API RESTful.
- psycopg2 : Pour la connexion et l'exécution de requêtes SQL sur une base de données PostgreSQL.
"""

from flask import Blueprint, jsonify, request       # type: ignore
from flask_restx import Resource, fields, Namespace # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
import psycopg2.extras                              # type: ignore
from psycopg2 import IntegrityError                 # type: ignore
from connect_db import DBConnection


climat_type_controller = Blueprint('climat_type_controller', __name__)
climat_type_namespace = Namespace('climat_type', description='Gestion des types de climat')

climat_type_model = climat_type_namespace.model('ClimatType', {
    'id_climat_type': fields.Integer(readonly=True, description='ID du type de climat'),
    'name': fields.String(required=True, description='Nom du type de climat'),
    'description': fields.String(description='Description du type de climat')
})

@climat_type_controller.route('/climat_types', methods=['GET'])
@jwt_required()
def get_all_climat_types():
    """
    Récupère tous les types de climat de la base de données.

    Retourne une liste de types de climat en format JSON.

    :return: Liste des types de climat en JSON, ou une erreur si une exception survient.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM climat_type")
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['GET'])
@jwt_required()
def get_climat_type_by_id(climat_type_id):
    """
    Récupère un type de climat spécifique par son ID.

    :param climat_type_id: ID du type de climat à récupérer.
    :return: Détails du type de climat en JSON, ou une erreur si le type de climat n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM climat_type WHERE id_climat_type = %s", (climat_type_id,))
            climat_type = cursor.fetchone()
            return jsonify(climat_type) if climat_type else (jsonify({"error": "Climat type not found"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_controller.route('/climat_type/name/<string:climat_type_name>', methods=['GET'])
@jwt_required()
def get_climat_type_by_name(climat_type_name):
    """
    Récupère un type de climat spécifique par son nom.

    :param climat_type_name: Nom du type de climat à récupérer.
    :return: Détails du type de climat en JSON, ou une erreur si le type de climat n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM climat_type WHERE name = %s", (climat_type_name,))
            climat_type = cursor.fetchone()
            if not climat_type:
                return jsonify({"error": "Climat type not found"}), 404
            return jsonify(climat_type), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_controller.route('/climat_type', methods=['POST'])
@jwt_required()
def create_climat_type():
    """
    Crée un nouveau type de climat dans la base de données.

    :return: Détails du type de climat créé avec un code de statut 201, ou une erreur si une exception survient.
    """
    try:
        data = request.json
        if "name" not in data:
            return jsonify({"error": "Missing 'name'"}), 400
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_climat_type FROM climat_type WHERE name = %s", (data["name"],))
            if cursor.fetchone():
                return jsonify({"error": "Climat type with this name already exists"}), 409
            cursor.execute(
                "INSERT INTO climat_type (name, description) VALUES (%s, %s) RETURNING id_climat_type", 
                (data["name"], data.get("description"))
            )
            new_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({"id_climat_type": new_id, "name": data["name"], "description": data.get("description")}), 201
    except IntegrityError:
        return jsonify({"error": "Duplicate climat type ID or name"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['PUT'])
@jwt_required()
def update_climat_type(climat_type_id):
    """
    Met à jour un type de climat spécifique par son ID.

    :param climat_type_id: ID du type de climat à mettre à jour.
    :return: Message de succès de mise à jour ou une erreur si le type de climat n'existe pas.
    """
    try:
        data = request.json
        if "name" not in data:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE climat_type
                SET name = %s, description = %s
                WHERE id_climat_type = %s
                RETURNING id_climat_type
                """,
                (data["name"], data.get("description"), climat_type_id)
            )
            if not cursor.fetchone():
                return jsonify({"error": "Climat type not found"}), 404
            conn.commit()
            return jsonify({"message": "Climat type updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['DELETE'])
@jwt_required()
def delete_climat_type(climat_type_id):
    """
    Supprime un type de climat spécifique par son ID.

    :param climat_type_id: ID du type de climat à supprimer.
    :return: Message de succès de suppression ou une erreur si le type de climat n'est pas trouvé.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM climat_type WHERE id_climat_type = %s RETURNING id_climat_type",
                (climat_type_id,)
            )
            deleted = cursor.fetchone()
            conn.commit()

            if not deleted:
                return jsonify({"error": "Climat type not found"}), 404
            return jsonify({"message": "Climat type deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@climat_type_namespace.route('/climat_types')
class ClimatTypes(Resource):
    """
    Classe API pour récupérer tous les types de climat.
    """
    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Récupère tous les types de climat.")
    @climat_type_namespace.marshal_list_with(climat_type_model)
    def get(self):
        """
        Récupère la liste de tous les types de climat.

        :return: Liste des types de climat en JSON si trouvée, ou une erreur avec un code 404 si aucun type de
        climat n'est trouvé.
        """
        response, status_code = get_all_climat_types()
        if status_code != 200:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json()

@climat_type_namespace.route('/climat_type')
class ClimatTypePost(Resource):
    """
    Classe API pour créer un nouveau type de climat.
    """
    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Crée un type de climat.")
    @climat_type_namespace.expect(climat_type_model)
    def post(self):
        """
        Crée un nouveau type de climat avec les données fournies.

        :return: Détails du type de climat créé en JSON avec un code de statut 201 si la création réussit,
                 ou une erreur avec un code de statut approprié si la création échoue.
        """
        response, status_code = create_climat_type()
        if status_code != 201:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json(), status_code

@climat_type_namespace.route('/climat_type/<int:climat_type_id>')
class ClimatTypeById(Resource):
    """
    Classe API pour récupérer, mettre à jour et supprimer un type de climat par son ID.
    """
    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Récupère un type de climat par ID.")
    @climat_type_namespace.marshal_with(climat_type_model)
    def get(self, climat_type_id):
        """
        Récupère un type de climat spécifique par son ID.

        :param climat_type_id: L'ID du type de climat à récupérer.
        :return: Détails du type de climat en JSON si trouvé, ou une erreur avec un code 404 si non trouvé.
        """
        response, status_code = get_climat_type_by_id(climat_type_id)
        if status_code != 200:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json()

    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Met à jour un type de climat.")
    @climat_type_namespace.expect(climat_type_model)
    def put(self, climat_type_id):
        """
        Met à jour un type de climat spécifique par son ID.

        :param climat_type_id: L'ID du type de climat à mettre à jour.
        :return: Détails du type de climat mis à jour en JSON si réussi, ou une erreur avec un code 404 si le
        type de climat n'est pas trouvé.
        """
        response, status_code = update_climat_type(climat_type_id)
        if status_code != 200:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json(), status_code

    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Supprime un type de climat.")
    def delete(self, climat_type_id):
        """
        Supprime un type de climat spécifique par son ID.

        :param climat_type_id: L'ID du type de climat à supprimer.
        :return: Message de confirmation en JSON si la suppression réussit, ou une erreur avec un code 404 si
        le type de climat n'est pas trouvé.
        """
        response, status_code = delete_climat_type(climat_type_id)
        if status_code != 200:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json(), status_code

@climat_type_namespace.route('/climat_type/name/<string:climat_type_name>')
class ClimatTypeByName(Resource):
    """
    Classe API pour récupérer un type de climat par son nom.
    """
    @jwt_required()
    @climat_type_namespace.doc(security="Bearer", description="Récupère un type de climat par nom.")
    @climat_type_namespace.marshal_with(climat_type_model)
    def get(self, climat_type_name):
        """
        Récupère un type de climat spécifique par son nom.

        :param climat_type_name: Le nom du type de climat à récupérer.
        :return: Détails du type de climat en JSON si trouvé, ou une erreur avec un code 404 si non trouvé.
        """
        response, status_code = get_climat_type_by_name(climat_type_name)
        if status_code != 200:
            climat_type_namespace.abort(status_code, response.get_json().get("error", "Erreur inconnue"))
        return response.get_json()
