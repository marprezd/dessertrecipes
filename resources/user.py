# resources/user.py file
from flask import request
from flask_restful import Resource
from http import HTTPStatus

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
