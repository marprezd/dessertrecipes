from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from http import HTTPStatus
from models.recipe import Recipe
from schemas.recipe import RecipeSchema

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)


class RecipeListResource(Resource):
    def get(self):
        """getting all recipes
        :return:
        """
        recipes = Recipe.get_all_published()

        return recipe_list_schema.dump(recipes).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        """method to gets all the recipe details"""
        json_data = request.get_json()
        current_user = get_jwt_identity()

        # verify data received
        data, errors = recipe_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        # If verification passes, create a Recipe object
        recipe = Recipe(**data)

        # ... then save the recipe
        recipe.user_id = current_user
        recipe.save()

        # converted recipe to JSON with a HTTP status code 201 CREATED message
        return recipe_schema.dump(recipe).data, HTTPStatus.CREATED


class RecipeResource(Resource):
    @jwt_optional
    def get(self, recipe_id):
        """This method get a specific recipe"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if recipe.is_publish is False and recipe.user_id != current_user:  # we use an access control
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # returns the recipe data in JSON format and the HTTP status code 200 OK if everything goes well.
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def patch(self, recipe_id):
        """This method update the recipe details"""
        json_data = request.get_json()
        data, errors = recipe_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        # check whether the recipe exists and whether the user has update privileges
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # update the recipe details and save it to the database
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()

        # returns the recipe data in JSON format and the HTTP status code 200 OK if everything goes well.
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        """This method is for deleting a recipe"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        # check whether the recipe exists and whether the user has update privileges
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.delete()

        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):
    @jwt_required
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        # Only users who have logged in can publish their own recipes
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = True
        recipe.save()

        # return HTTPStatus.NO_CONTENT, which shows us that the recipe has been published successfully
        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, recipe_id):
        """implementing delete method"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        # Only an authenticated user can unpublish the recipe
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = False
        recipe.save()

        # return HTTPStatus.NO_CONTENT, which shows us that the recipe has been unpublished successfully
        return {}, HTTPStatus.NO_CONTENT
