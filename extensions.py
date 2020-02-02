# extensions.py file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# instance of SQLAlchemy object
db = SQLAlchemy()
# instance of Flask JWT Extended object
jwt = JWTManager()

