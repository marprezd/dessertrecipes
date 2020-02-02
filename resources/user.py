# resources/user.py file
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required

from utils import hash_password
from models.user import User


class UserListResource(Resource):
    """implement the Post method"""

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
    """Define a get method and wrap it with a jwt_optional decorator."""

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
