from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required     # type: ignore
from datetime import datetime, timedelta
from connect_db import DBConnection, get_db_connection

prediction_namespace = Namespace('prediction', description="Gestion des prédictions")

prediction_model = prediction_namespace.model('Prediction', {
    'id_prediction': fields.Integer(readonly=True),
    'id_country': fields.Integer,
    'id_disease': fields.Integer,
    'ds': fields.String(description='Date de la prédiction'),

    'yhat': fields.Float,
    'yhat_lower': fields.Float,
    'yhat_upper': fields.Float,

    'trend': fields.Float,
    'trend_lower': fields.Float,
    'trend_upper': fields.Float,

    'deaths': fields.Float,
    'deaths_lower': fields.Float,
    'deaths_upper': fields.Float,

    'pib': fields.Float,
    'pib_lower': fields.Float,
    'pib_upper': fields.Float,

    'population': fields.Float,
    'population_lower': fields.Float,
    'population_upper': fields.Float
})

@prediction_namespace.route('/predictions/get')
class PredictionResource(Resource):
    @jwt_required()
    @prediction_namespace.response(200, 'Succès')
    @prediction_namespace.response(400, 'Requête invalide')
    @prediction_namespace.response(500, 'Erreur serveur')
    def get(self):
        """Récupérer les prédictions par maladie entre deux dates, si la période est valide"""
        try:
            disease_id = request.args.get('disease_id')
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            country_id = request.args.get('country_id')

            if not disease_id or not start_date_str or not end_date_str:
                return {'msg': "Paramètres requis : disease_id, start_date, end_date"}, 400

            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return {'msg': "Les dates doivent être au format YYYY-MM-DD"}, 400

            today = datetime.today().date()
            max_end_date = today + timedelta(days=90)

            if end_date > max_end_date:
                return {'msg': "La date de fin ne peut pas dépasser 3 mois à partir d'aujourd'hui"}, 400

            with DBConnection() as conn:
                cur = conn.cursor()
                
                query = """
                    SELECT 
                        id_prediction, id_country, id_disease, ds,
                        ROUND(yhat), ROUND(yhat_lower), ROUND(yhat_upper),
                        trend, trend_lower, trend_upper,
                        ROUND(deaths), ROUND(deaths_lower), ROUND(deaths_upper),
                        pib, pib_lower, pib_upper,
                        ROUND(population), ROUND(population_lower), ROUND(population_upper)
                    FROM prediction
                    WHERE id_disease = %s
                    AND ds BETWEEN %s AND %s
                """
                params = [disease_id, start_date, end_date]
                
                if country_id:
                    query += " AND id_country = %s"
                    params.append(country_id)
                    
                query += " ORDER BY ds ASC, id_country ASC, id_prediction ASC;"
                
                cur.execute(query, params)

                rows = cur.fetchall()

                predictions = []
                for row in rows:
                    predictions.append({
                        'id_prediction': row[0],
                        'id_country': row[1],
                        'id_disease': row[2],
                        'ds': row[3].strftime('%Y-%m-%d'),

                        'yhat': row[4],
                        'yhat_lower': row[5],
                        'yhat_upper': row[6],

                        'trend': row[7],
                        'trend_lower': row[8],
                        'trend_upper': row[9],

                        'deaths': row[10],
                        'deaths_lower': row[11],
                        'deaths_upper': row[12],

                        'pib': row[13],
                        'pib_lower': row[14],
                        'pib_upper': row[15],

                        'population': row[16],
                        'population_lower': row[17],
                        'population_upper': row[18],
                    })

                return predictions, 200

        except Exception as e:
            return {'msg': "Erreur serveur"}, 500

@prediction_namespace.route('/predictions/transmission-rate')
class TransmissionRateResource(Resource):

    conn = get_db_connection()

    def get_new_cases(self, country_id, disease_id, date, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT yhat
                FROM prediction
                WHERE id_country = %s AND id_disease = %s AND ds = %s
            """, (country_id, disease_id, date))
            result = cur.fetchone()
            return result[0] if result else 0.0

    def get_total_cases(self, country_id, disease_id, date, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT SUM(yhat)
                FROM prediction
                WHERE id_country = %s AND id_disease = %s AND ds <= %s
            """, (country_id, disease_id, date))
            result = cur.fetchone()
            return result[0] if result and result[0] is not None else 0.0

    @jwt_required()
    @prediction_namespace.response(200, 'Succès')
    @prediction_namespace.response(400, 'Requête invalide')
    @prediction_namespace.response(500, 'Erreur serveur')
    def get(self):
        country_id = request.args.get('country_id')
        disease_id = request.args.get('disease_id')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not country_id or not disease_id:
            return {"error": "Paramètres 'country_id' et 'disease_id' requis"}, 400

        try:
            start_date_str = start_date_str[:10]
            end_date_str = end_date_str[:10]
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            result_list = []

            current_date = start_date
            while current_date <= end_date:
                previous_day = current_date - timedelta(days=1)

                new_cases = self.get_new_cases(country_id, disease_id, current_date, self.conn)
                total_cases = self.get_total_cases(country_id, disease_id, previous_day, self.conn)

                rate = new_cases / total_cases if total_cases > 0 else 0.0

                result_list.append({str(current_date): rate})
                current_date += timedelta(days=1)

            return {
                "country_id": country_id,
                "disease_id": disease_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "transmission_rate": result_list
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500


@prediction_namespace.route('/predictions/mortality-rate')
class MortalityRateResource(Resource):

    conn = get_db_connection()

    def get_country_population(self, country_id, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT population FROM country WHERE id_country = %s
            """, (country_id,))
            result = cur.fetchone()
            return result[0] if result and result[0] else 0

    def get_daily_mortality_rate(self, country_id, disease_id, date, conn, population):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT deaths
                FROM prediction
                WHERE id_country = %s AND id_disease = %s AND ds = %s
            """, (country_id, disease_id, date))
            result = cur.fetchone()
            if result and result[0] is not None and population and population != 0:
                return result[0] / population
            return 0.0

    @jwt_required()
    @prediction_namespace.response(200, 'Succès')
    @prediction_namespace.response(400, 'Requête invalide')
    @prediction_namespace.response(500, 'Erreur serveur')
    def get(self):
        country_id = request.args.get('country_id')
        disease_id = request.args.get('disease_id')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not country_id or not disease_id or not start_date_str or not end_date_str:
            return {"error": "Paramètres 'country_id', 'disease_id', 'start_date' et 'end_date' requis"}, 400

        try:
            start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()

            population = self.get_country_population(country_id, self.conn)
            if population == 0:
                return {"error": "Population non trouvée pour ce pays"}, 500

            mortality_rates = []
            current_date = start_date
            while current_date <= end_date:
                rate = self.get_daily_mortality_rate(country_id, disease_id, current_date, self.conn, population)
                mortality_rates.append({str(current_date): rate})
                current_date += timedelta(days=1)

            return {
                "country_id": country_id,
                "disease_id": disease_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "mortality_rate": mortality_rates
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500