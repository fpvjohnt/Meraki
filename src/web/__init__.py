from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from web.config import Config
import logging

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Register Blueprints
    from web.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    @app.route('/')
    def hello():
        return "Hello, Meraki Health Check!"

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Server Error: %s', str(error))
        return jsonify(error=str(error)), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', str(e))
        return jsonify(error=str(e)), 500

    return app