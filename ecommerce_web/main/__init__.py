from flask import Flask, jsonify
from flask_cors import CORS
from main.config.config import Config
from main.extension import db, bcrypt, migrate
from main.config.routes import register_routes  # Import route registration function


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db, compare_type=True)

    # Register all routes
    register_routes(app)

    return app
