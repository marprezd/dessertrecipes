# resources/token.py file
from http import HTTPStatus
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from utils import check_password
from models.user import User


class TokenResource(Resource):
    """This class inherits from flask_restful.Resource"""
    def post(self):
        """
        When a user logs in, this method will be invoked and it will take the email and password from the client
        JSON request.
        """
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')

        user = User.get_by_email(email=email)  # Verify the correctness of the user's credentials

        if not user or not check_password(password, user.password):
            # Return 401 UNAUTHORIZED, with an email message.
            return {'message': 'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED

        # Create an access token with the user id as the identity to the user.
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, HTTPStatus.OK
