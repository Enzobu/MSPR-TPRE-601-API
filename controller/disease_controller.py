"""
Contrôleur Flask pour gérer les routes liées aux maladies. Ce module expose des API REST permettant
de créer, lire, mettre à jour et supprimer des maladies dans une base de données.

Les routes sont organisées en plusieurs classes, chaque classe étant responsable d'une opération spécifique
liée aux maladies (ex: récupérer une maladie par ID, créer une nouvelle maladie, etc.). Chaque route
interagit avec la base de données pour effectuer les opérations CRUD (Create, Read, Update, Delete).

Les méthodes de la classe contrôleur retournent des réponses sous forme de dictionnaires JSON, avec des
codes HTTP appropriés pour indiquer le succès ou l'échec des opérations. Les erreurs sont également gérées
et renvoient des messages d'erreur détaillés en cas de problème avec les requêtes ou la base de données.

Les principales opérations exposées par ce module incluent :
    - Récupérer toutes les maladies.
    - Récupérer une maladie par son ID ou son nom.
    - Créer une nouvelle maladie.
    - Mettre à jour une maladie existante.
    - Supprimer une maladie.

Chaque route et méthode dispose d'un modèle de données (Disease) utilisé pour la validation et la
présentation des informations des maladies dans les réponses de l'API.

Modules et dépendances utilisés :
    - Flask : framework web pour créer les routes et gérer les requêtes HTTP.
    - Flask-RESTx : pour exposer l'API REST et sérialiser les données.
    - psycopg2 : pour interagir avec la base de données PostgreSQL.
    - DBConnection : module personnalisé pour la gestion des connexions à la base de données.

Exemple d'utilisation de chaque méthode :
    - GET /diseases : récupère toutes les maladies.
    - GET /disease/<id> : récupère une maladie par son ID.
    - GET /disease/name/<name> : récupère une maladie par son nom.
    - POST /disease : crée une nouvelle maladie.
    - PUT /disease/<id> : met à jour une maladie existante.
    - DELETE /disease/<id> : supprime une maladie par son ID.
"""

from flask import Blueprint, request                # type: ignore
from flask_restx import Namespace, Resource, fields # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
import psycopg2.extras                              # type: ignore
from connect_db import DBConnection


disease_controller = Blueprint('disease_controller', __name__)

disease_namespace = Namespace('disease', description='Gestion des maladies')

disease_model = disease_namespace.model('Disease', {
    'id_disease': fields.Integer(readonly=True, description='ID de la maladie'),
    'name': fields.String(required=True, description='Nom de la maladie'),
    'is_pandemic': fields.Boolean(required=True, description='Indique si la maladie est une pandémie')
})

@disease_controller.route('/diseases', methods=['GET'])
@jwt_required()
def get_all_diseases():
    """
    Récupère toutes les maladies présentes dans la base de données.

    Returns:
        list: Liste des maladies avec les détails.
        int: Code HTTP de la réponse (200 si tout va bien, 500 en cas d'erreur).
    """
    print("Fetching all diseases")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM disease")
            diseases = cursor.fetchall()
            return diseases, 200
    except Exception as e:
        print(f"Error fetching diseases: {e}")
        return {"error": str(e)}, 500

@disease_controller.route('/disease/<int:disease_id>', methods=['GET'])
@jwt_required()
def get_disease_by_id(disease_id):
    """
    Récupère une maladie spécifique par son ID.

    Args:
        disease_id (int): ID de la maladie à récupérer.

    Returns:
        dict: Détails de la maladie demandée.
        int: Code HTTP de la réponse (200 si trouvé, 404 si non trouvé, 500 en cas d'erreur).
    """
    print(f"Fetching disease with ID: {disease_id}")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM disease WHERE id_disease = %s", (disease_id,))
            disease = cursor.fetchone()
            if not disease:
                return {"error": f"Disease with ID {disease_id} not found"}, 404
            return disease, 200
    except Exception as e:
        print(f"Error fetching disease by ID: {e}")
        return {"error": f"An error occurred: {str(e)}"}, 500

@disease_controller.route('/disease/name/<string:disease_name>', methods=['GET'])
@jwt_required()
def get_disease_by_name(disease_name):
    """
    Récupère une maladie par son nom.

    Args:
        disease_name (str): Nom de la maladie à récupérer.

    Returns:
        dict: Détails de la maladie demandée.
        int: Code HTTP de la réponse (200 si trouvé, 404 si non trouvé, 500 en cas d'erreur).
    """
    print(f"Fetching disease with name: {disease_name}")
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM disease WHERE name = %s", (disease_name,))
            disease = cursor.fetchone()
            if not disease:
                return {"error": f"Disease named '{disease_name}' not found"}, 404
            return disease, 200
    except Exception as e:
        print(f"Error fetching disease by name: {e}")
        return {"error": f"An error occurred: {str(e)}"}, 500

@disease_controller.route('/disease', methods=['POST'])
@jwt_required()
def create_disease():
    """
    Crée une nouvelle maladie dans la base de données.

    Returns:
        dict: Détails de la maladie créée avec l'ID.
        int: Code HTTP de la réponse (201 si créé avec succès, 500 en cas d'erreur).
    """
    data = request.json
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO disease (name, is_pandemic)
                VALUES (%s, %s) RETURNING id_disease
                """,
                (data['name'], data['is_pandemic'])
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return {"id_disease": new_id}, 201
    except Exception as e:
        print(f"Error creating disease: {e}")
        return {"error": str(e)}, 500

@disease_controller.route('/disease/<int:disease_id>', methods=['PUT'])
@jwt_required()
def update_disease(disease_id):
    """
    Met à jour les informations d'une maladie existante.

    Args:
        disease_id (int): ID de la maladie à mettre à jour.

    Returns:
        dict: Message de confirmation ou erreur.
        int: Code HTTP de la réponse (200 si mis à jour, 404 si non trouvé, 500 en cas d'erreur).
    """
    data = request.json
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE disease
                SET name = %s, is_pandemic = %s
                WHERE id_disease = %s
                RETURNING id_disease
            """, (
                data['name'],
                data['is_pandemic'],
                disease_id
            ))
            updated = cursor.fetchone()
            conn.commit()
            if not updated:
                print("Disease not found for update")
                return {"error": "Disease not found"}, 404
            print("Disease updated successfully")
            return {"message": "Disease updated successfully"}, 200
    except Exception as e:
        print(f"Error updating disease: {e}")
        return {"error": str(e)}, 500

@disease_controller.route('/disease/<int:disease_id>', methods=['DELETE'])
@jwt_required()
def delete_disease(disease_id):
    """
    Supprime une maladie par son ID.

    Args:
        disease_id (int): ID de la maladie à supprimer.

    Returns:
        dict: Message de confirmation ou erreur.
        int: Code HTTP de la réponse (200 si supprimé, 404 si non trouvé, 500 en cas d'erreur).
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM disease WHERE id_disease = %s RETURNING id_disease", (disease_id,))
            deleted = cursor.fetchone()
            conn.commit()
            if not deleted:
                print("Disease not found for deletion")
                return {"error": "Disease not found"}, 404
            print("Disease deleted successfully")
            return {"message": "Disease deleted successfully"}, 200
    except Exception as e:
        print(f"Error deleting disease: {e}")
        return {"error": str(e)}, 500

@disease_namespace.route('/diseases')
class Diseases(Resource):
    """
    Classe pour récupérer toutes les maladies.
    """
    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Récupère toutes les maladies.")
    @disease_namespace.marshal_list_with(disease_model)
    def get(self):
        """
        Récupère la liste de toutes les maladies.

        :return: Une liste des maladies en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = get_all_diseases()
        if status_code != 200:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response

@disease_namespace.route('/disease/<int:disease_id>')
class DiseaseById(Resource):
    """
    Classe pour récupérer, mettre à jour ou supprimer une maladie par son ID.
    """
    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Récupère une maladie par ID.")
    @disease_namespace.marshal_with(disease_model)
    def get(self, disease_id):
        """
        Récupère une maladie spécifique à partir de son ID.

        :param disease_id: L'ID de la maladie à récupérer.
        :return: Les détails de la maladie en JSON avec un code de statut 200 si trouvé,
                 ou une erreur avec un code de statut 404 si non trouvée.
        """
        response, status_code = get_disease_by_id(disease_id)
        if status_code != 200:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response

    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Met à jour une maladie existante.")
    @disease_namespace.expect(disease_model)
    def put(self, disease_id):
        """
        Met à jour une maladie spécifique à partir de son ID.

        :param disease_id: L'ID de la maladie à mettre à jour.
        :return: Les détails de la maladie mise à jour en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si la maladie n'existe pas.
        """
        response, status_code = update_disease(disease_id)
        if status_code != 200:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Supprime une maladie par ID.")
    def delete(self, disease_id):
        """
        Supprime une maladie spécifique à partir de son ID.

        :param disease_id: L'ID de la maladie à supprimer.
        :return: Un message de confirmation en JSON avec un code de statut 200 si réussi,
                 ou une erreur avec un code de statut 404 si la maladie n'existe pas.
        """
        response, status_code = delete_disease(disease_id)
        if status_code != 200:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code

@disease_namespace.route('/disease/name/<string:disease_name>')
class DiseaseByName(Resource):
    """
    Classe pour récupérer une maladie par son nom.
    """
    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Récupère une maladie par nom.")
    @disease_namespace.marshal_with(disease_model)
    def get(self, disease_name):
        """
        Récupère une maladie spécifique à partir de son nom.

        :param disease_name: Le nom de la maladie à récupérer.
        :return: Les détails de la maladie en JSON avec un code de statut 200 si trouvée,
                 ou une erreur avec un code de statut 404 si non trouvée.
        """
        response, status_code = get_disease_by_name(disease_name)
        if status_code != 200:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response

@disease_namespace.route('/disease')
class DiseasePost(Resource):
    """
    Classe pour créer une nouvelle maladie.
    """
    @jwt_required()
    @disease_namespace.doc(security='Bearer', description="Crée une nouvelle maladie.")
    @disease_namespace.expect(disease_model)
    def post(self):
        """
        Crée une nouvelle maladie.

        :return: Les détails de la maladie créée en JSON avec un code de statut 201 si réussi,
                 ou une erreur avec un code de statut approprié en cas d'échec.
        """
        response, status_code = create_disease()
        if status_code != 201:
            disease_namespace.abort(status_code, response.get("error", "Erreur inconnue"))
        return response, status_code
