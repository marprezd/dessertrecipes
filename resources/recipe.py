from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional


class RecipeListResource(Resource):
    """implementing the RecipeListResource class, which inherits from flask-restful.Resource."""

    def get(self):
        """getting all recipes"""
        recipes = Recipe.get_all_published()
        data = []

        for recipe in recipes:
            data.append(recipe.data())

        return {'data': data}, HTTPStatus.OK

    @jwt_required
    def post(self):
        """
        gets all the recipe details from the client requests and
        saves them in the database
        """
        json_data = request.get_json()
        current_user = get_jwt_identity()

        recipe = Recipe(
            name=json_data['name'],
            description=json_data['description'],
            num_of_servings=json_data['num_of_servings'],
            cook_time=json_data['cook_time'],
            directions=json_data['directions'],
            user_id=current_user
        )

        recipe.save()

        # returns the recipe record with an HTTP status code 201 CREATED
        return recipe.data(), HTTPStatus.CREATED


class RecipeResource(Resource):
    """implementing the RecipeResource class, which inherits from flask-restful.Resource."""

    @jwt_optional
    def get(self, recipe_id):
        """This method get a specific recipe"""
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if recipe.is_publish is False and recipe.user_id != current_user:  # we use an access control
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return recipe.data(), HTTPStatus.OK

    @jwt_required
    def put(self, recipe_id):
        """This method update the recipe details"""
        json_data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        # check whether the recipe exists and whether the user has update privileges
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        # update the recipe details and save it to the database
        recipe.name = json_data['name']
        recipe.description = json_data['description']
        recipe.num_of_servings = json_data['num_of_servings']
        recipe.cook_time = json_data['cook_time']
        recipe.directions = json_data['directions']

        recipe.save()

        # returns the HTTP status code 200 OK if everything goes well.
        return recipe.data(), HTTPStatus.OK

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
    """implementing put method"""
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
