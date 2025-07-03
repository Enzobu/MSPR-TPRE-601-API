from flask import request                           # type: ignore
from flask_restx import Namespace, Resource, fields # type: ignore
from flask_jwt_extended import jwt_required         # type: ignore
from connect_db import get_db_connection
from decimal import Decimal

log_namespace = Namespace('metrics', description="Gestion des métriques")

# Modèle complet pour la réponse
metrics_response_model = log_namespace.model('MetricsResponse', {
    'id_metrics': fields.Integer(description="ID du log", example=45),
    '_date': fields.String(description="Date du log", example="2025-06-30"),
    'is_sucess': fields.Boolean(description="État", example=True),
    'error_string': fields.String(description="Message d'erreur", example="Lorem ipsum dolor sit amet"),
    'id_country': fields.Raw(description="Données du pays concerné", example={
        "id_country": 4,
        "name": "France",
        "iso_code": "FR",
        "population": 68000000,
        "pib": 3200000000,
        "latitude": 48.8,
        "longitude": 2.3,
        "id_continent": 1,
        "id_region": 3
    })
})

error_model = log_namespace.model('ErrorResponse', {
    'error': fields.String(description="Message d'erreur", example="Une erreur est survenue")
})

@log_namespace.route('/log/get')
class MetricsByCountryResource(Resource):

    @jwt_required()
    @log_namespace.response(200, 'Succès', metrics_response_model)
    @log_namespace.response(400, 'Requête invalide', error_model)
    @log_namespace.response(500, 'Erreur serveur', error_model)
    def get(self):
        """
        Récupère les métriques d'un pays et les moyennes R² et R² bis du continent correspondant.
        """
        try:
            id_country = request.args.get('id_country')

            def to_float(val):
                if isinstance(val, Decimal):
                    return float(val)
                return val

            conn = get_db_connection()
            with conn.cursor() as cur:
                # Récupérer la dernière métrique du pays
                if id_country:
                    cur.execute("""
                        SELECT 
                            l.id_log, l._date, l.is_success, l.error_string,
                            c.id_country, c.name, c.iso_code, c.population, c.pib, c.latitude, c.longitude, c.id_continent, c.id_region
                        FROM log l
                        INNER JOIN country c ON l.id_country = c.id_country
                        WHERE l.id_country = %s
                        ORDER BY l._date DESC
                        LIMIT 1
                    """, (id_country,))
                    log_row = cur.fetchone()

                    if not log_row:
                        return {"error": "Aucune métrique trouvée pour le pays donné"}, 400

                    return {
                        "id_log": log_row[0],
                        "_date": log_row[1].strftime("%Y-%m-%d"),
                        "is_success": log_row[2],
                        "error_string": log_row[3],
                        "country": {
                            "id_country": log_row[4],
                            "name": log_row[5],
                            "iso_code": log_row[6],
                            "population": to_float(log_row[7]),
                            "pib": to_float(log_row[8]),
                            "latitude": to_float(log_row[9]),
                            "longitude": to_float(log_row[10]),
                            "id_continent": log_row[11],
                            "id_region": log_row[12]
                        }
                    }, 200
                else:
                    cur.execute("""
                        SELECT 
                            l.id_log, l._date, l.is_success, l.error_string,
                            c.id_country, c.name, c.iso_code, c.population, c.pib, c.latitude, c.longitude, c.id_continent, c.id_region
                        FROM log l
                        INNER JOIN country c ON l.id_country = c.id_country
                        ORDER BY l._date DESC
                    """)
                    log_rows = rows = cur.fetchall()

                    if not log_rows:
                        return {"error": "Aucune métrique trouvée pour le pays donné"}, 400

                    results = []
                    for log_row in log_rows:
                        results.append({
                            "id_log": log_row[0],
                            "_date": log_row[1].strftime("%Y-%m-%d"),
                            "is_success": log_row[2],
                            "error_string": log_row[3],
                            "country": {
                                "id_country": log_row[4],
                                "name": log_row[5],
                                "iso_code": log_row[6],
                                "population": to_float(log_row[7]),
                                "pib": to_float(log_row[8]),
                                "latitude": to_float(log_row[9]),
                                "longitude": to_float(log_row[10]),
                                "id_continent": log_row[11],
                                "id_region": log_row[12]
                            }
                        })

                    return results, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            conn.close()
