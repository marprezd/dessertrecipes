# extensions.py file

# Import the necessary package and module
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, IMAGES
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create an instance of SQLAlchemy object
db = SQLAlchemy()
# Create an instance of Flask JWT Extended object
jwt = JWTManager()
# Create an instance of Flask Upload object
image_set = UploadSet('images', IMAGES)
# Create an instance of Flask Cache object
cache = Cache()
# Create an instance of Limiter object
limiter = Limiter(key_func=get_remote_address)