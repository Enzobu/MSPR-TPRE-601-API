
"""
Contrôleur Flask pour la gestion des régions.

Ce module implémente un contrôleur Flask avec une API RESTful pour gérer les régions dans une base de données
PostgreSQL.
Il fournit des points d'API pour récupérer, créer, mettre à jour et supprimer des régions, ainsi que pour
récupérer une région spécifique par son ID ou son nom.

Points d'API disponibles :
- GET /regions : Récupère toutes les régions.
- GET /region/<int:region_id> : Récupère une région spécifique par son ID.
- GET /region/name/<string:region_name> : Récupère une région par son nom.
- POST /region : Crée une nouvelle région.
- PUT /region/<int:region_id> : Met à jour une région existante.
- DELETE /region/<int:region_id> : Supprime une région.

Le module utilise SQLAlchemy pour la gestion des bases de données et Flask-RESTX pour la documentation de
l'API et le modèle de sérialisation.

Modules utilisés :
- Flask : Framework web léger pour créer des API.
- Flask-RESTX : Extension Flask pour créer des API RESTful avec documentation intégrée.
- psycopg2 : Bibliothèque pour se connecter à une base de données PostgreSQL.
- connect_db : Module pour établir la connexion à la base de données.

Fonctionnalités principales :
- Récupération des régions depuis la base de données.
- Création, mise à jour et suppression de régions.
- Gestion des erreurs et des messages appropriés pour les réponses API.

Exemple de réponse pour GET /regions :
{
    "id_region": 1,
    "name": "Île-de-France"
}

Exemple de réponse pour POST /region :
{
    "id_region": 2,
    "name": "Provence-Alpes-Côte d'Azur"
}

"""

from flask import Blueprint, jsonify, request       # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
from flask_restx import Namespace, Resource, fields # type: ignore
import psycopg2.extras                              # type: ignore
from flask_restx import reqparse                    # type: ignore
from connect_db import DBConnection


region_controller = Blueprint('region_controller', __name__)

region_namespace = Namespace('region', description='Gestion des régions')

region_model = region_namespace.model('Region', {
    'id_region': fields.Integer(readOnly=True, description='ID de la région'),
    'name': fields.String(required=True, description='Nom de la région')
})

region_parser = reqparse.RequestParser()
region_parser.add_argument("name", type=str, required=True, help="Nom de la région", location="json")

def fetch_regions():
    """
    Récupère toutes les régions de la base de données.

    Retourne une liste de dictionnaires représentant les régions.

    :return: Liste des régions
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM region")
            regions = cursor.fetchall()
            return regions
    except Exception as e:
        print("Erreur lors de la récupération des données des régions :", e)
        return []

@region_controller.route('/regions', methods=['GET'])
@jwt_required()
def get_regions():
    """
    Récupère toutes les régions.

    :return: Liste des régions avec un statut HTTP 200, ou un message d'erreur 404 si aucune
    région trouvée.
    """
    regions = fetch_regions()
    if not regions:
        return jsonify({"error": "No regions found"}), 404
    return regions, 200

@region_controller.route('/region/<int:region_id>', methods=['GET'])
@jwt_required()
def get_region(region_id):
    """
    Récupère une région spécifique par son ID.

    :param region_id: ID de la région à récupérer
    :return: Détails de la région avec un statut HTTP 200, ou un message d'erreur 404 si la région
    n'existe pas.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM region WHERE id_region = %s", (region_id,))
            region = cursor.fetchone()
            if not region:
                return jsonify({"error": "Region not found"}), 404
            return region, 200
    except Exception as e:
        print("Erreur lors de la récupération des données de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

@region_controller.route('/region/name/<string:region_name>', methods=['GET'])
@jwt_required()
def get_region_by_name(region_name):
    """
    Récupère une région spécifique par son nom.

    :param region_name: Nom de la région à récupérer
    :return: Détails de la région avec un statut HTTP 200, ou un message d'erreur 404 si la région
    n'existe pas.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM region WHERE name = %s", (region_name,))
            region = cursor.fetchone()
            if not region:
                return jsonify({"error": f"Region named '{region_name}' not found"}), 404
            return region, 200
    except Exception as e:
        print("Erreur lors de la récupération de la région par nom :", e)
        return jsonify({"error": "An error occurred"}), 500

@region_controller.route('/region', methods=['POST'])
@jwt_required()
def create_region():
    """
    Crée une nouvelle région.

    :return: Détails de la région créée avec un statut HTTP 201, ou un message d'erreur 400 si un champ
    est manquant.
    """
    try:
        new_region = request.json
        if "name" not in new_region:
            return {"error": "Missing 'name'"}, 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO region (name) VALUES (%s) RETURNING id_region",
                (new_region["name"],)
            )
            new_region_id = cursor.fetchone()[0]
            conn.commit()

        return {
            "id_region": new_region_id,
            "name": new_region["name"]
        }, 201

    except Exception as e:
        print("Erreur lors de la création de la région :", e)
        return {"error": "An error occurred"}, 500

    except Exception as e:
        print("Erreur lors de la création de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

@region_controller.route('/region/<int:region_id>', methods=['PUT'])
@jwt_required()
def update_region(region_id):
    """
    Met à jour les informations d'une région existante.

    :param region_id: ID de la région à mettre à jour
    :return: Détails de la région mise à jour avec un statut HTTP 200, ou un message d'erreur 404 si la
    région n'existe pas.
    """
    try:
        updated_region = request.json

        if "name" not in updated_region:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE region
                SET name = %s
                WHERE id_region = %s
                RETURNING id_region, name
                """,
                (
                    updated_region["name"],
                    region_id
                )
            )
            updated_region_data = cursor.fetchone()
            if not updated_region_data:
                return jsonify({"error": "Region not found"}), 404

            conn.commit()

        return jsonify({
            "id_region": updated_region_data[0],
            "name": updated_region_data[1]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

@region_controller.route('/region/<int:region_id>', methods=['DELETE'])
@jwt_required()
def delete_region(region_id):
    """
    Supprime une région existante.

    :param region_id: ID de la région à supprimer
    :return: Message de confirmation avec un statut HTTP 200, ou un message d'erreur 404 si la région
    n'existe pas.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM region WHERE id_region = %s RETURNING id_region", (region_id,))
            deleted_region = cursor.fetchone()

            if not deleted_region:
                return jsonify({"error": "Region not found"}), 404

            conn.commit()

        return jsonify({"message": f"Region with ID {region_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

@region_namespace.route('/regions')
class Regions(Resource):
    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Récupère toutes les régions.")
    @region_namespace.marshal_list_with(region_model)
    def get(self):
        return get_regions()[0]

@region_namespace.route('/region')
class RegionPost(Resource):
    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Crée une nouvelle région.")
    @region_namespace.expect(region_parser)
    def post(self):
        response, status_code = create_region()
        if status_code != 201:
            region_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

@region_namespace.route('/region/<int:region_id>')
class Region(Resource):
    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Récupère une région spécifique par ID.")
    @region_namespace.marshal_with(region_model)
    def get(self, region_id):
        return get_region(region_id)[0]

    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Met à jour une région existante.")
    @region_namespace.expect(region_parser)
    def put(self, region_id):
        return update_region(region_id)[0]

    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Supprime une région.")
    def delete(self, region_id):
        return delete_region(region_id)[0]

@region_namespace.route('/region/name/<string:region_name>')
class RegionByName(Resource):
    @jwt_required()
    @region_namespace.doc(security='Bearer', description="Récupère une région par nom.")
    @region_namespace.marshal_with(region_model)
    def get(self, region_name):
        return get_region_by_name(region_name)[0]