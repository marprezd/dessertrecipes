# app.py file
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from config import Config
from extensions import db, jwt
from resources.user import UserListResource, UserResource, MeResource
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.token import TokenResource

migrate = Migrate()


def create_app():
    """function to create the Flask app, also invoke the register_extensions and register_resources functions"""
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    """function to initialize SQLAlchemy, Flask-JWT-Extended and set up Flask-Migrate"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


def register_resources(app):
    """function to set up resource routing"""
    api = Api(app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(TokenResource, '/token')
    api.add_resource(MeResource, '/me')


if __name__ == '__main__':
    app = create_app()
    app.run()  # start the application
