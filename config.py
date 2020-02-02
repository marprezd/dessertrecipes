# config.py file
class Config:
    """Define path database, debug & track modifications and add a variables"""
    DEBUG = True  # set True for debugging purposes

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://marpezdev:l1021257@localhost/data_recipe'  # path of the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configure Flask-JWT-Extend
    SECRET_KEY = 'super-secret-key'
    JWT_ERROR_MESSAGE_KEY = 'message'
