import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .config import flask_config
from .cache import Cache

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=os.getenv('FLASK_ENV', 'production')):
    app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER', '../dist'), static_url_path='/')
    app.config.from_prefixed_env()
    app.config.from_object(flask_config[config_name])

    app.cache = Cache(app)
    
    db.init_app(app)
    from . import models
    
    migrate.init_app(app, db, directory='./migrations')

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .blueprints import api as api_bp
    app.register_blueprint(api_bp)
    
    return app
