"""
Module Flask pour la gestion de la relation pays-types de climat.
Ce module fournit une API REST permettant de récupérer, créer, mettre à jour et supprimer 
des relations entre les pays et leurs types de climat.

Dépendances :
- Flask
- Flask-RESTx
- psycopg2 (pour la connexion à la base de données PostgreSQL)
"""

from flask import Blueprint, jsonify, request       # type: ignore
from flask_restx import Resource, fields, Namespace # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
import psycopg2.extras                              # type: ignore
from connect_db import DBConnection

# Définition du Blueprint et du Namespace
country_climat_type_controller = Blueprint('country_climat_type_controller', __name__)
country_climat_type_namespace = Namespace('country_climat_type', description='Gestion des relations pays-types de climat')

# Modèle pour la documentation de l'API
documentation_model = country_climat_type_namespace.model('CountryClimatType', {
    'id_climat_type': fields.Integer(required=True, description='Identifiant du type de climat'),
    'id_country': fields.Integer(required=True, description='Identifiant du pays associé'),
})

@country_climat_type_controller.route('/country_climat_types', methods=['GET'])
@jwt_required()
def get_all_country_climat_types():
    """Récupère toutes les relations pays-types de climat."""
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM country_climat_type")
            result = cursor.fetchall()
            return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@country_climat_type_controller.route('/country_climat_type/<int:id_climat_type>/<int:id_country>', methods=['GET'])
@jwt_required()
def get_country_climat_type(id_climat_type, id_country):
    """Récupère une relation spécifique entre un pays et un type de climat."""
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM country_climat_type WHERE id_climat_type = %s AND id_country = %s", (id_climat_type, id_country))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Relation not found"}), 404

            return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@country_climat_type_controller.route('/country_climat_type', methods=['POST'])
@jwt_required()
def create_country_climat_type():
    """Ajoute une nouvelle relation entre un pays et un type de climat."""
    try:
        data = request.json
        if "id_climat_type" not in data or "id_country" not in data:
            return jsonify({"error": "Missing 'id_climat_type' or 'id_country'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO country_climat_type (id_climat_type, id_country) VALUES (%s, %s) RETURNING id_climat_type, id_country",
                (data["id_climat_type"], data["id_country"])
            )
            new_entry = cursor.fetchone()
            conn.commit()

        return jsonify({
            "id_climat_type": new_entry[0],
            "id_country": new_entry[1]
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@country_climat_type_controller.route('/country_climat_type/<int:id_climat_type>/<int:id_country>', methods=['PUT'])
@jwt_required()
def update_country_climat_type(id_climat_type, id_country):
    """Met à jour une relation entre un pays et un type de climat."""
    try:
        data = request.json
        if "new_id_climat_type" not in data or "new_id_country" not in data:
            return jsonify({"error": "Missing 'new_id_climat_type' or 'new_id_country'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE country_climat_type
                SET id_climat_type = %s, id_country = %s
                WHERE id_climat_type = %s AND id_country = %s
                RETURNING id_climat_type, id_country
                """,
                (data["new_id_climat_type"], data["new_id_country"], id_climat_type, id_country)
            )
            updated = cursor.fetchone()
            conn.commit()

            if not updated:
                return jsonify({"error": "Relation not found"}), 404

            return jsonify({"message": "Relation updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@country_climat_type_controller.route('/country_climat_type/<int:id_climat_type>/<int:id_country>', methods=['DELETE'])
@jwt_required()
def delete_country_climat_type(id_climat_type, id_country):
    """Supprime une relation entre un pays et un type de climat."""
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM country_climat_type WHERE id_climat_type = %s AND id_country = %s RETURNING id_climat_type, id_country",
                (id_climat_type, id_country)
            )
            deleted = cursor.fetchone()
            conn.commit()

            if not deleted:
                return jsonify({"error": "Relation not found"}), 404

            return jsonify({"message": "Relation deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@country_climat_type_namespace.route('/country_climat_types')
class CountryClimatTypesResource(Resource):
    """Ressource pour récupérer toutes les relations pays-types de climat."""
    @jwt_required()
    @country_climat_type_namespace.doc(security='Bearer', description="Récupère toutes les relations pays-types de climat.")
    @country_climat_type_namespace.marshal_list_with(documentation_model)
    def get(self):
        return get_all_country_climat_types()[0]

@country_climat_type_namespace.route('/country_climat_type')
class CountryClimatTypesResource(Resource):
    """Ressource pour récupérer toutes les relations pays-types de climat."""
    @jwt_required()
    @country_climat_type_namespace.doc(security='Bearer', description="Ajoute une nouvelle relation pays-type de climat.")
    @country_climat_type_namespace.expect(documentation_model)
    def post(self):
        return create_country_climat_type()[0]

@country_climat_type_namespace.route('/country_climat_type/<int:id_climat_type>/<int:id_country>')
class CountryClimatTypeResource(Resource):
    """Ressource pour gérer une relation pays-type de climat spécifique."""
    @jwt_required()
    @country_climat_type_namespace.doc(security='Bearer', description="Récupère une relation pays-type de climat spécifique.")
    @country_climat_type_namespace.marshal_with(documentation_model)
    def get(self, id_climat_type, id_country):
        return get_country_climat_type(id_climat_type, id_country)[0]

    @jwt_required()
    @country_climat_type_namespace.doc(security='Bearer', description="Met à jour une relation pays-type de climat.")
    @country_climat_type_namespace.expect(documentation_model)
    def put(self, id_climat_type, id_country):
        return update_country_climat_type(id_climat_type, id_country)[0]

    @jwt_required()
    @country_climat_type_namespace.doc(security='Bearer', description="Supprime une relation pays-type de climat.")
    def delete(self, id_climat_type, id_country):
        return delete_country_climat_type(id_climat_type, id_country)[0]
