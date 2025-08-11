from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .config import Config
from .cache import Cache

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.cache = Cache(app)
    
    db.init_app(app)
    from . import models
    
    migrate.init_app(app, db, directory='./migrations')

    @app.cli.command
    def createdb():
        db.create_all()
    
    from .blueprints import api as api_bp
    app.register_blueprint(api_bp)
    
    return app
