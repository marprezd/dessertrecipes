# config.py file

# Import the necessary package and module
import os


class Config:
    # Set False for disable debugging
    DEBUG = False

    # Define track modifications
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configure Flask-JWT-Extend
    JWT_ERROR_MESSAGE_KEY = 'message'

    # Configure logout functionality
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # Set the image destination folder
    UPLOADED_IMAGES_DEST = 'static/images'

    # Set caching-related
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10*60

    # Set rate limit
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    # Set True for debugging purposes
    DEBUG = True

    # Define path database
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://marpezdev:l1021257@localhost/data_recipe'  # path of the database

    # Configure Flask-JWT-Extend
    SECRET_KEY = 'super-secret-key'


class ProductionConfig(Config):
    # imitate the production environment for testing
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class StagingConfig(Config):

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')