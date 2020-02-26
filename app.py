# app.py file

# Import the necessary package and module
import os
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class

from config import Config
from extensions import db, jwt, image_set, cache, limiter

from resources.user import (
    UserListResource, UserResource,
    MeResource, UserRecipeListResource,
    UserActivateResource, UserAvatarUploadResource
)
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list
from resources.recipe import (
    RecipeListResource, RecipeResource,
    RecipePublishResource, RecipeCoverUploadResource
)


migrate = Migrate()


def create_app():
    """function to get the configurations dynamically,
    also invoke the register_extensions and register_resources functions"""
    env = os.environ.get('ENV', 'Production')

    if env == 'Production':
        config_str = 'config.ProductionConfig'
    elif env == 'Staging':
        config_str = 'config.StagingConfig'
    else:
        config_str = 'config.DevelopmentConfig'

    app = Flask(__name__)
    app.config.from_object(config_str)

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    """function to initialize extensions"""
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    patch_request_class(app, 10*1024*1024)
    cache.init_app(app)
    limiter.init_app(app)

    # check whether the token is on the blacklist
    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']

        return jti in black_list


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
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(RecipeCoverUploadResource, '/recipes/<int:recipe_id>/cover')


# Uncomment only for put your IP address in a white list to test the RESTful APIs Web Service
# @limiter.request_filter
# def ip_whitelist():
#     return request.remote_addr == '127.0.0.1'


# Running the application
if __name__ == '__main__':
    app = create_app()
    app.run()
