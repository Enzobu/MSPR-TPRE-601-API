from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required  # type: ignore
from connect_db import get_db_connection
from decimal import Decimal

metric_namespace = Namespace('metrics', description="Gestion des métriques")

# Modèle complet pour la réponse
metrics_response_model = metric_namespace.model('MetricsResponse', {
    'id_metrics': fields.Integer(description="ID de la métrique", example=45),
    '_date': fields.String(description="Date de la métrique", example="2025-06-30"),
    'rmse': fields.Float(description="RMSE", example=25684.35),
    'mae': fields.Float(description="MAE", example=1574.25),
    'r2': fields.Float(description="R²", example=0.92),
    'rmse_bis': fields.Float(description="RMSE bis", example=1684.35),
    'mae_bis': fields.Float(description="MAE bis", example=874.25),
    'r2_bis': fields.Float(description="R² bis", example=0.98),
    'continent': fields.String(description="Nom du continent", example="Europe"),
    'continent_r2': fields.Float(description="Moyenne du R² du continent", example=78.95),
    'continent_r2_bis': fields.Float(description="Moyenne du R² bis du continent", example=96.95),
})

error_model = metric_namespace.model('ErrorResponse', {
    'error': fields.String(description="Message d'erreur", example="Une erreur est survenue")
})


@metric_namespace.route('/metrics/get')
class MetricsByCountryResource(Resource):

    @jwt_required()
    @metric_namespace.response(200, 'Succès', metrics_response_model)
    @metric_namespace.response(400, 'Requête invalide', error_model)
    @metric_namespace.response(500, 'Erreur serveur', error_model)
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
                cur.execute("""
                    SELECT m.id_metrics, m._date, m.rmse, m.mae, m.r2, m.rmse_bis, m.mae_bis, m.r2_bis,
                           co.name as continent_name
                    FROM metrics m
                    INNER JOIN country c ON m.id_country = c.id_country
                    INNER JOIN continent co ON c.id_continent = co.id_continent
                    WHERE c.id_country = %s
                    ORDER BY m._date DESC
                    LIMIT 1
                """, (id_country,))
                metric_row = cur.fetchone()

                if not metric_row:
                    return {"error": "Aucune métrique trouvée pour le pays donné"}, 400

                (id_metrics, _date, rmse, mae, r2, rmse_bis, mae_bis, r2_bis, continent_name) = metric_row

                # Calculer la moyenne des r2 et r2_bis sur le continent
                cur.execute("""
                    SELECT AVG(m.r2), AVG(m.r2_bis)
                    FROM metrics m
                    INNER JOIN country c ON m.id_country = c.id_country
                    INNER JOIN continent co ON c.id_continent = co.id_continent
                    WHERE LOWER(co.name) = LOWER(%s)
                """, (continent_name,))
                avg_result = cur.fetchone()

                continent_r2 = round(to_float(avg_result[0]), 4) if avg_result[0] is not None else None
                continent_r2_bis = round(to_float(avg_result[1]), 4) if avg_result[1] is not None else None

            return {
                "id_metrics": id_metrics,
                "_date": _date.strftime("%Y-%m-%d") if hasattr(_date, "strftime") else _date,
                "rmse": to_float(rmse),
                "mae": to_float(mae),
                "r2": round(to_float(r2), 4) if r2 is not None else None,
                "rmse_bis": to_float(rmse_bis),
                "mae_bis": to_float(mae_bis),
                "r2_bis": round(to_float(r2_bis), 4) if r2_bis is not None else None,
                "continent": continent_name,
                "continent_r2": continent_r2,
                "continent_r2_bis": continent_r2_bis
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            conn.close()
