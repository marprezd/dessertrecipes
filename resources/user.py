# resources/user.py file

# Import the necessary package and module
import os
from flask import request, url_for, render_template
from flask_restful import Resource
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from http import HTTPStatus

from extensions import image_set, limiter

from mailgun import MailgunApi
from models.user import User
from models.recipe import Recipe

from schemas.recipe import RecipeSchema, RecipePaginationSchema
from schemas.user import UserSchema

from utils import generate_token, verify_token, save_image, clear_cache

from webargs import fields
from webargs.flaskparser import use_kwargs

user_schema = UserSchema()
user_avatar_schema = UserSchema(only=('avatar_url',))
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)
recipe_pagination_schema = RecipePaginationSchema()

# This data is stored in the environment variable. First, you should ensure of
# creating an account with Mailgun, then generate the API_KEY and API_URL,
# and add both to the environment variable.
mailgun = MailgunApi(
    domain=os.environ.get('MAILGUN_DOMAIN'),
    api_key=os.environ.get('MAILGUN_API_KEY'))

# Create a dictionary for API pagination. The key-value pairs are passed to the
# @use_kwargs decorator
pages = {
    'page': fields.Int(missing=1),
    'per_page': fields.Int(missing=10),
    'visibility': fields.Str(missing='public')
}


class UserListResource(Resource):
    def post(self):
        """This method has the logic to add new users"""
        json_data = request.get_json()

        data, errors = user_schema.load(data=json_data)

        # Verify data entry. Email and username must be unique.
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):  # check if user already exists in the database
            return {'message': 'Username already used'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(data.get('email')):  # check if email already exists in the database
            return {'message': 'Email already used'}, HTTPStatus.BAD_REQUEST

        # Create a user object
        user = User(**data)

        # Save the user object
        user.save()

        # Generate a token to activate the user account
        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration.'

        # Create the activation link and message to activate account
        link = url_for('useractivateresource', token=token, _external=True)
        text = 'Hi, Thanks for using DessertRecipe! Please confirm your registration\
        by clicking on the link: {}'.format(link)

        # Send the email
        mailgun.send_email(
            to=user.email,
            subject=subject,
            text=text,
            html=render_template('email/send-activation.html', link=link))

        # Return the user details in JSON format
        return user_schema.dump(user).data, HTTPStatus.CREATED


class UserResource(Resource):
    @jwt_optional
    def get(self, username):
        """This method has the logic to retrieve a user"""
        user = User.get_by_username(username=username)

        # Check whether the username can be found in the database.
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()  # check whether it matches the identity of the user ID in the JWT.

        #  Access control. Show sensitive information only if the user ID associated with the data to
        #  be retrieved is identical to the user currently logged in
        if current_user == user.id:
            data = user_schema.dump(user).data
        else:
            data = user_public_schema.dump(user).data

        return data, HTTPStatus.OK


class MeResource(Resource):
    @jwt_required
    def get(self):
        """This method has the logic to get the user information by the ID in the JWT"""
        user = User.get_by_id(id=get_jwt_identity())

        return user_schema.dump(user).data, HTTPStatus.OK


class UserRecipeListResource(Resource):
    decorators = [limiter.limit('3/minute; 30/hour; 300/day', methods=['GET'], error_message='Too Many Request')]

    @jwt_optional
    @use_kwargs(pages)
    def get(self, username, page, per_page, visibility):
        """This method has the logic to retrieve all recipes published by a user."""
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

        # Gets the paginated recipes by a particular author
        paginated_recipes = Recipe.get_all_by_user(user_id=user.id, page=page, per_page=per_page, visibility=visibility)

        # Serialize the paginated object and return HTTP Status Code
        return recipe_pagination_schema.dump(paginated_recipes).data, HTTPStatus.OK


class UserActivateResource(Resource):
    def get(self, token):
        """This method has the logic to verify the token, email and the user account status"""
        email = verify_token(token, salt='activate')

        if email is False:
            return {'message': 'Invalid token or token expired'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_email(email=email)

        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        # If the user account is already activated
        if user.is_active is True:
            return {'message': 'The user account is already activated'}, HTTPStatus.BAD_REQUEST

        user.is_active = True

        user.save()

        # Request was handled successfully
        return {}, HTTPStatus.NO_CONTENT


class UserAvatarUploadResource(Resource):
    @jwt_required
    def put(self):
        """This method has the logic to put the user avatar image file"""
        file = request.files.get('avatar')

        # Validate image
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_id(id=get_jwt_identity())

        if user.avatar_image:
            avatar_path = image_set.path(folder='avatar', filename=user.avatar_image)

            # Check is avatar exist and removed before we replace it with our uploaded image
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        # Save image
        filename = save_image(image=file, folder='avatars')

        # Store the filename of image withing 'user.avatar_image'
        user.avatar_image = filename

        # Save image update to the database
        user.save()

        # Clear cache
        clear_cache('/recipes')

        # Finally, return the URL image in a JSON format and with status code HTTP 200 OK
        return user_avatar_schema.dump(user).data, HTTPStatus.OK
