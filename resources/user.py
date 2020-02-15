# resources/user.py file
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from http import HTTPStatus

from models.user import User
from models.recipe import Recipe

from schemas.recipe import RecipeSchema
from schemas.user import UserSchema

from utils import hash_password

from webargs import fields
from webargs.flaskparser import use_kwargs

user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)


class UserListResource(Resource):
    def post(self):
        """function to get the JSON formatted data in the request"""
        json_data = request.get_json()

        username = json_data.get('username')
        email = json_data.get('email')
        non_hash_password = json_data.get('password')

        if User.get_by_username(username):  # check if user already exists in the database
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(email):  # check if email already exists in the database
            return {'message': 'email already used'}, HTTPStatus.BAD_REQUEST

        # hash the password
        password = hash_password(non_hash_password)

        # create user object
        user = User(
            username=username,
            email=email,
            password=password
        )

        # save the user object
        user.save()

        # return the user details in JSON format
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }

        return data, HTTPStatus.CREATED


class UserResource(Resource):
    @jwt_optional
    def get(self, username):
        """check whether the username can be found in the database."""
        user = User.get_by_username(username=username)
        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()  # check whether it matches the identity of the user ID in the JWT.

        #  Access control and output different information
        if current_user == user.id:
            data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        else:
            data = {
                'id': user.id,
                'username': user.username
            }

        return data, HTTPStatus.OK


class MeResource(Resource):
    @jwt_required
    def get(self):
        """get the user information by the ID in the JWT"""
        user = User.get_by_id(id=get_jwt_identity())
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

        return data, HTTPStatus.OK


class UserRecipeListResource(Resource):
    @jwt_optional
    @use_kwargs({'visibility': fields.Str(missing='public')})
    def get(self, username, visibility):
        """we will implement access control"""
        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        # If the username is the currently authenticated user, then they can
        # see all the recipes
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'

        recipes = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)

        # convert the recipes into JSON format and return HTTP Status Code
        return recipe_list_schema.dump(recipes).data, HTTPStatus.OK
