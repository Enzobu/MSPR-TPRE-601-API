"""
Contrôleur pour gérer les statements dans l'application.

Ce module permet de récupérer, créer, mettre à jour et supprimer des statements
dans la base de données à travers des routes API.
"""

from flask import Blueprint, jsonify, request       # type: ignore
from flask_restx import Namespace, Resource, fields # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
import psycopg2.extras                              # type: ignore
from connect_db import DBConnection


statement_controller = Blueprint('statement_controller', __name__)

statement_namespace = Namespace('statement', description='Gestion des statements')

statement_model = statement_namespace.model('Statement', {
    'id_statement': fields.Integer(readOnly=True, description='ID du statement'),
    '_date': fields.Date(required=True, description='Date du statement'),
    'confirmed': fields.Integer(required=True, description='Cas confirmés'),
    'deaths': fields.Integer(required=True, description='Nombre de décès'),
    'recovered': fields.Integer(required=True, description='Nombre de récupérés'),
    'active': fields.Integer(required=True, description='Nombre de cas actifs'),
    'total_tests': fields.Integer(description='Total des tests effectués'),
    'id_disease': fields.Integer(required=True, description='ID de la maladie'),
    'id_country': fields.Integer(required=True, description='ID du pays')
})

pagination_parser = statement_namespace.parser()
pagination_parser.add_argument('page', type=int, required=False, default=1, help='Numéro de la page')
pagination_parser.add_argument('per_page', type=int, required=False, default=100, help="Nombre d'éléments par page")

def fetch_statements(page=1, per_page=100):
    try:
        offset = (page - 1) * per_page
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM statement
                ORDER BY id_statement
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            return cursor.fetchall()
    except Exception as e:
        print("Erreur lors de la récupération des données des statements :", e)
        return []

@statement_controller.route('/statements', methods=['GET'])
@jwt_required()
def get_statements():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=100, type=int)
    statements = fetch_statements(page, per_page)
    if not statements:
        return jsonify({"error": "No statements found"}), 404
    return jsonify(statements), 200

@statement_controller.route('/statement/<int:statement_id>', methods=['GET'])
@jwt_required()
def get_statement(statement_id):
    """
    Route pour récupérer un statement spécifique par son ID.

    Args:
        statement_id (int): L'ID du statement à récupérer.

    Returns:
        Response: Statement en format JSON ou message d'erreur.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM statement WHERE id_statement = %s", (statement_id,))
            statement = cursor.fetchone()
            if not statement:
                return jsonify({"error": "Statement not found"}), 404
            return statement, 200
    except Exception as e:
        print("Erreur lors de la récupération des données du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

@statement_controller.route('/statement', methods=['POST'])
@jwt_required()
def create_statement():
    """
    Route pour créer un nouveau statement.

    Returns:
        Response: Le statement créé en format JSON ou message d'erreur.
    """
    try:
        new_statement = request.json

        required_fields = [
            "_date",
            "confirmed",
            "deaths",
            "recovered",
            "active",
            "id_disease",
            "id_country"
        ]
        for field in required_fields:
            if field not in new_statement:
                return jsonify({"error": f"Missing '{field}'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO statement (
                    _date,
                    confirmed,
                    deaths,
                    recovered,
                    active,
                    total_tests,
                    id_disease,
                    id_country
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_statement
                """,
                (
                    new_statement["_date"],
                    new_statement["confirmed"],
                    new_statement["deaths"],
                    new_statement["recovered"],
                    new_statement["active"],
                    new_statement.get("total_tests"),
                    new_statement["id_disease"],
                    new_statement["id_country"]
                )
            )
            new_statement_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_statement": new_statement_id,
            "_date": new_statement["_date"],
            "confirmed": new_statement["confirmed"],
            "deaths": new_statement["deaths"],
            "recovered": new_statement["recovered"],
            "active": new_statement["active"],
            "total_tests": new_statement.get("total_tests"),
            "id_disease": new_statement["id_disease"],
            "id_disease": new_statement["id_country"]
        }), 201

    except Exception as e:
        print("Erreur lors de la création du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

@statement_controller.route('/statement/<int:statement_id>', methods=['PUT'])
@jwt_required()
def update_statement(statement_id):
    """
    Route pour mettre à jour un statement existant.

    Args:
        statement_id (int): L'ID du statement à mettre à jour.

    Returns:
        Response: Statement mis à jour en format JSON ou message d'erreur.
    """
    try:
        updated_statement = request.json

        required_fields = [
            "_date",
            "confirmed",
            "deaths",
            "recovered",
            "active",
            "id_disease",
            "id_country"
        ]
        for field in required_fields:
            if field not in updated_statement:
                return jsonify({"error": f"Missing '{field}'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE statement
                SET _date = %s,
                    confirmed = %s,
                    deaths = %s,
                    recovered = %s,
                    active = %s,
                    total_tests = %s,
                    id_disease = %s,
                    id_country = %s
                WHERE id_statement = %s
                RETURNING
                    id_statement,
                    _date,
                    confirmed,
                    deaths,
                    recovered,
                    active,
                    total_tests,
                    id_disease,
                    id_country
                """,
                (
                    updated_statement["_date"],
                    updated_statement["confirmed"],
                    updated_statement["deaths"],
                    updated_statement["recovered"],
                    updated_statement["active"],
                    updated_statement.get("total_tests"),
                    updated_statement["id_disease"],
                    updated_statement["id_country"],
                    statement_id
                )
            )
            updated_statement_data = cursor.fetchone()
            if not updated_statement_data:
                return jsonify({"error": "Statement not found"}), 404

            conn.commit()

        return jsonify({
            "id_statement": updated_statement_data[0],
            "_date": updated_statement_data[1],
            "confirmed": updated_statement_data[2],
            "deaths": updated_statement_data[3],
            "recovered": updated_statement_data[4],
            "active": updated_statement_data[5],
            "total_tests": updated_statement_data[6],
            "id_disease": updated_statement_data[7],
            "id_disease": updated_statement_data[8]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

@statement_controller.route('/statement/<int:statement_id>', methods=['DELETE'])
@jwt_required()
def delete_statement(statement_id):
    """
    Route pour supprimer un statement spécifique par son ID.

    Args:
        statement_id (int): L'ID du statement à supprimer.

    Returns:
        Response: Message de confirmation de suppression ou message d'erreur.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM statement WHERE id_statement = %s RETURNING id_statement",
                (statement_id,)
            )
            deleted_statement = cursor.fetchone()

            if not deleted_statement:
                return jsonify({"error": "Statement not found"}), 404

            conn.commit()

        return jsonify({"message": f"Statement with ID {statement_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

@statement_namespace.route('/statements')
class Statements(Resource):
    @jwt_required()
    @statement_namespace.doc(security='Bearer', description="Récupère tous les statements avec pagination.")
    @statement_namespace.expect(pagination_parser)
    @statement_namespace.marshal_list_with(statement_model)
    def get(self):
        args = pagination_parser.parse_args()
        page = args.get('page')
        per_page = args.get('per_page')
        return fetch_statements(page, per_page)

@statement_namespace.route('/statement')
class StatementPost(Resource):
    """
    Ressource pour gérer la création de statement.
    """
    @jwt_required()
    @statement_namespace.doc(security='Bearer', description="Crée un nouveau statement.")
    @statement_namespace.expect(statement_model)
    def post(self):
        """
        Crée un nouveau statement.

        Returns:
            Response: Statement créé en format JSON.
        """
        return create_statement()[0]

@statement_namespace.route('/statement/<int:statement_id>')
class Statement(Resource):
    """
    Ressource pour gérer l'accès à un statement spécifique par son ID.
    """
    @jwt_required()
    @statement_namespace.doc(security='Bearer', description="Récupère un statement spécifique par ID.")
    @statement_namespace.marshal_with(statement_model)
    def get(self, statement_id):
        """
        Récupère un statement par son ID.

        Args:
            statement_id (int): L'ID du statement à récupérer.

        Returns:
            Response: Statement en format JSON.
        """
        return get_statement(statement_id)[0]

    @jwt_required()
    @statement_namespace.doc(security='Bearer', description="Met à jour un statement existant.")
    @statement_namespace.expect(statement_model)
    def put(self, statement_id):
        """
        Met à jour un statement existant.

        Args:
            statement_id (int): L'ID du statement à mettre à jour.

        Returns:
            Response: Statement mis à jour en format JSON.
        """
        return update_statement(statement_id)[0]

    @jwt_required()
    @statement_namespace.doc(security='Bearer', description="Supprime un statement.")
    def delete(self, statement_id):
        """
        Supprime un statement spécifique.

        Args:
            statement_id (int): L'ID du statement à supprimer.

        Returns:
            Response: Message de confirmation de suppression.
        """
        return delete_statement(statement_id)[0]
