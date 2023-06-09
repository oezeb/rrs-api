import json
import logging
import os
import secrets

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, send_from_directory
from flask_cors import CORS

from . import admin_api, api, auth, db, models, user_api, util


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(),
        DB_HOST=os.environ.get('DB_HOST'),
        DB_PORT=os.environ.get('DB_PORT'),
        DATABASE=os.environ.get('DATABASE'),
        DB_USER=os.environ.get('DB_USER'),
        DB_PASSWORD=os.environ.get('DB_PASSWORD'),
    )
    app.url_map.strict_slashes = False

    if test_config is not None:
        app.config.from_mapping(test_config)
    

    spec = APISpec(
        title='Reservation System',
        version='1.0.0',
        openapi_version='3.0.0',
        info=dict(title='Reservation System', version='1.0.0'),
        plugins=[FlaskPlugin(), MarshmallowPlugin()]
    )
    
    db.init_app(app)
    api.init_api(app, spec)
    auth.init_auth(app, spec)
    user_api.init_api(app, spec)
    admin_api.init_api(app, spec)
    init_api_docs(app, spec)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("server.log"),
            logging.StreamHandler()
        ],
        format="%(asctime)s %(levelname)s %(name)s : %(message)s"
    )

    return app

def init_api_docs(app, spec):
    os.makedirs(app.instance_path, exist_ok=True)
    with open(os.path.join(app.instance_path, 'docs.json'), 'w') as f:
        json.dump(spec.to_dict(), f)

    @app.route('/api/docs.json')
    @auth.auth_required(role=db.UserRole.ADMIN)
    def docs():
        """Serve api docs
        ---
        get:
          summary: Serve api docs
          description: Serve api docs
          tags:
            - Admin
          responses:
            200:
              description: OK
              content:
                application/json:
                  schema:
                    type: object
        """
        return send_from_directory(app.instance_path, 'docs.json')
    
    with app.test_request_context():
        spec.path(view=docs)

__all__ = ['create_app', 'models', 'db', 'api', 'auth', 'user_api', 'admin_api', 'util']
