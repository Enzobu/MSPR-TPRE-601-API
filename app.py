"""
Main Flask application for MSPR 601 API: manages health and climate data.
"""

import sys
from datetime import timedelta

import bcrypt
from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from controller import climat_type_controller, continent_controller, country_climat_type_controller
from controller import country_controller, disease_controller, region_controller, statement_controller
from controller import login_controller, prediction_controller, metric_controller, log_controller
from connect_db import get_db_connection


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


PASSWORD_TO_HASH = "password"
hashed_password_str = hash_password(PASSWORD_TO_HASH)

print(f"Hashed password: {hashed_password_str}")

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'your_super_secure_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
jwt = JWTManager(app)


@app.route('/')
def home():
    """Homepage that confirms the API is working."""
    return {"message": "API is working correctly"}, 200


authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Add 'Bearer <your_token>' in the request header"
    }
}

api = Api(
    app,
    title="MSPR 502 API",
    version="1.0",
    description="API documentation for managing health and weather data.",
    doc="/api/docs",
    authorizations=authorizations,
    security='Bearer'
)

# Adding namespaces for Swagger documentation
api.add_namespace(climat_type_controller.climat_type_namespace, path='/swagger')
api.add_namespace(continent_controller.continent_namespace, path='/swagger')
api.add_namespace(country_controller.country_namespace, path='/swagger')
api.add_namespace(country_climat_type_controller.country_climat_type_namespace, path='/swagger')
api.add_namespace(disease_controller.disease_namespace, path='/swagger')
api.add_namespace(region_controller.region_namespace, path='/swagger')
api.add_namespace(statement_controller.statement_namespace, path='/swagger')
api.add_namespace(login_controller.user_namespace, path='/swagger')
api.add_namespace(prediction_controller.prediction_namespace, path='/swagger')
api.add_namespace(metric_controller.metric_namespace, path='/swagger')
api.add_namespace(log_controller.log_namespace, path='/swagger')

# Database connection
db_connection = get_db_connection()
if not db_connection:
    print("Unable to connect to the database.")
    sys.exit(1)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    Protected route that requires a valid JWT token.
    """
    current_user = get_jwt_identity()
    return jsonify(message=f"Welcome, {current_user}!"), 200


# Registering blueprints for API routes
blueprints = [
    climat_type_controller.climat_type_controller,
    continent_controller.continent_controller,
    country_controller.country_controller,
    country_climat_type_controller.country_climat_type_controller,
    disease_controller.disease_controller,
    region_controller.region_controller,
    statement_controller.statement_controller,
]

for blueprint in blueprints:
    app.register_blueprint(blueprint, url_prefix='/api')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
