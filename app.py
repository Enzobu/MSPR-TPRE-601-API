import sys
import bcrypt                                                                                   # type: ignore
from flask import Flask, request, jsonify                                                       # type: ignore
from flask_restx import Api                  
from flask_cors import CORS                                                                     # type: ignore
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  # type: ignore
from controller import climat_type_controller, continent_controller, country_climat_type_controller
from controller import country_controller, disease_controller, region_controller, statement_controller
from controller import login_controller, prediction_controller
from connect_db import get_db_connection
from datetime import timedelta


def hash_password(password: str) -> str:
    """Hache un mot de passe en utilisant bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

password_to_hash = "password"
hashed_password = hash_password(password_to_hash)

print(f"Mot de passe haché : {hashed_password}")

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète_super_sécurisée'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
jwt = JWTManager(app)

@app.route('/')
def home():
    return {"message": "L'API fonctionne correctement"}, 200

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Ajouter 'Bearer <votre_token>' dans l'en-tête de la requête"
    }
}

api = Api(app,
          title="MSPR 502 API",
          version="1.0",
          description="Documentation de l'API pour la gestion des données sanitaires et météorologiques.",
          doc="/api/docs",
          authorizations=authorizations,
            security='Bearer'
          )

api.add_namespace(climat_type_controller.climat_type_namespace, path='/swagger')
api.add_namespace(continent_controller.continent_namespace, path='/swagger')
api.add_namespace(country_controller.country_namespace, path='/swagger')
api.add_namespace(country_climat_type_controller.country_climat_type_namespace, path='/swagger')
api.add_namespace(disease_controller.disease_namespace, path='/swagger')
api.add_namespace(region_controller.region_namespace, path='/swagger')
api.add_namespace(statement_controller.statement_namespace, path='/swagger')
api.add_namespace(login_controller.user_namespace, path='/swagger')
api.add_namespace(prediction_controller.prediction_namespace, path='/swagger')

db_connection = get_db_connection()
if not db_connection:
    print("Impossible de se connecter à la base de données.")
    sys.exit(1)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    Route protégée nécessitant un token JWT valide.
    """
    current_user = get_jwt_identity()
    return jsonify(message=f"Bienvenue, {current_user} !"), 200

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
