# resources/recipe.py file

# Import the necessary package and module
import os
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from http import HTTPStatus

from webargs import fields
from webargs.flaskparser import use_kwargs

from models.recipe import Recipe
from schemas.recipe import RecipeSchema, RecipePaginationSchema

from extensions import image_set, cache, limiter

from utils import save_image, clear_cache

# Instantiated and serialize an object
recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=('cover_url', ))
recipe_pagination_schema = RecipePaginationSchema()

# Create a dictionary for API pagination, search and ordering data.
# The key-value pairs are passed to the @use_kwargs decorator
pages = {
    'q': fields.Str(missing=''),
    'page': fields.Int(missing=1),
    'per_page': fields.Int(missing=20),
    'sort': fields.Str(missing='created_at'),
    'order': fields.Str(missing='desc')
}


class RecipeListResource(Resource):

    # Setting the number of requests to our RESTful APIs
    decorators = [limiter.limit('3/minute; 30/hour; 300/day', methods=['GET'], error_message='Too Many Requests')]

    @use_kwargs(pages)
    @cache.cached(timeout=60, query_string=True)
    def get(self, q, page, per_page, sort, order):
        """This method have the logic to retrieve
         all recipes, paginate, sort results and search for recipes"""

        # Accept only the created_at, cook_time, and num_of_servings values
        if sort not in ['created_at', 'cook_time', 'num_of_servings']:
            sort = 'created_at'

        # Accept only the asc and desc values
        if order not in ['asc', 'desc']:
            order = 'desc'

        paginated_recipes = Recipe.get_all_published(q, page, per_page, sort, order)

        return recipe_pagination_schema.dump(paginated_recipes).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        """This method has got the logic to add a new recipe"""
        json_data = request.get_json()
        current_user = get_jwt_identity()

        # Verify data received
        data, errors = recipe_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        # If verification passes, create a Recipe object
        recipe = Recipe(**data)

        # ... Then save the recipe
        recipe.user_id = current_user
        recipe.save()

        # Finally, return the recipe in a JSON format and with status code HTTP 201 CREATED
        return recipe_schema.dump(recipe).data, HTTPStatus.CREATED


class RecipeResource(Resource):
    @jwt_optional
    def get(self, recipe_id):
        """This method has got the logic to get a specific recipe"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        # We use an access control. If the current user is not the owner of the recipe and if
        # the recipe is not published
        if recipe.is_publish is False and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # Finally, return the recipe in a JSON format and with status code HTTP 200 OK
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def patch(self, recipe_id):
        """This method has got the logic to update the recipe details"""
        json_data = request.get_json()
        data, errors = recipe_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        # Check whether the recipe exists and whether the user has update privileges
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # Update the recipe details and then save them in the database
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()

        # Clear cache
        clear_cache('/recipes')

        # Finally, return the recipe in a JSON format and with status code HTTP 200 OK
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        """This method has the logic to delete a recipe that has been published"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        # Check whether the recipe exists and whether the user has privileges to delete it
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # Delete recipe
        recipe.delete()

        # Clear cache
        clear_cache('/recipes')

        # And return an empty JSON with status code HTTP NO_CONTENT
        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):

    @jwt_required
    def put(self, recipe_id):
        """This method has got the logic to publish a recipe"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        # Only users who have logged in can publish their own recipes
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = True
        recipe.save()

        # Clear cache
        clear_cache('/recipes')

        # And return an empty JSON with status code HTTP NO_CONTENT
        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, recipe_id):
        """This method has got the logic to unpublish a previously published recipe."""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        # Only an authenticated user can unpublished the recipe
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = False
        recipe.save()

        # Clear cache
        clear_cache('/recipes')

        # And return an empty JSON with status code HTTP NO_CONTENT
        return {}, HTTPStatus.NO_CONTENT


class RecipeCoverUploadResource(Resource):

    @jwt_required
    def put(self, recipe_id):
        """This method has got the logic to put the cover image of the recipe."""
        file = request.files.get('cover')

        # Check if cover image exists and whether the file extension is permitted
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        # Retrieved the Recipe object
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        # Check right to modify the recipe
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if recipe.cover_image:
            cover_path = image_set.path(folder='recipes', filename=recipe.cover_image)

            if os.path.exists(cover_path):
                os.remove(cover_path)

        # Save the uploaded image
        filename = save_image(image=file, folder='recipes')

        recipe.cover_image = filename

        # Save the recipe
        recipe.save()

        # Clear cache
        clear_cache('/recipes')

        # Finally, return the URL image in a JSON format and with status code HTTP 200 OK
        return recipe_cover_schema.dump(recipe).data, HTTPStatus.OK
