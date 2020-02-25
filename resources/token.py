# resources/token.py file

# Import the necessary package and module
from http import HTTPStatus
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from utils import check_password
from models.user import User

black_list = set()


class TokenResource(Resource):

    def post(self):
        """This method has the logic to receive the email together password of the client and
        generate an authentication token
        """
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')

        # Verify the correctness of the user's credentials
        user = User.get_by_email(email=email)

        if not user or not check_password(password, user.password):
            # Return 401 UNAUTHORIZED, with an email message.
            return {'message': 'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED

        # User cannot log in to the application before their account is activated
        if user.is_active is False:
            return {'message': 'The user account is not activated yet'}, HTTPStatus.FORBIDDEN

        # Create an access token with the user id as the identity to the user and pass
        # in the fresh=True parameter to the create_access_token function. We
        # then invoke the create_refresh_token function to generate a refresh token..
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.OK


class RefreshResource(Resource):
    @jwt_refresh_token_required
    def post(self):
        """This method has the logic to refresh a token for a previously
        authenticated user"""
        current_user = get_jwt_identity()
        token = create_access_token(identity=current_user, fresh=False)

        return {'token': token}, HTTPStatus.OK


class RevokeResource(Resource):

    @jwt_required
    def post(self):
        """This method has the logic to implementing the logout function"""
        jti = get_raw_jwt()['jti']

        # After getting the token we put it in the blacklist
        black_list.add(jti)

        return {'message': 'Successfully logged out'}, HTTPStatus.OK