import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'top-secret-key')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///catalog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True


flask_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}