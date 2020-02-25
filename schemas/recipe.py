# schemas/recipe.py file

# Import the necessary package and module
from flask import url_for
from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema
from schemas.pagination import PaginationSchema


def validate_num_of_servings(number):
    """This function has the logic to validate the 'num_of_servings' attribute"""
    if number < 1:
        raise ValidationError('Number of servings must be greater than 0.')
    if number > 50:
        raise ValidationError('Number of servings must not be greater than 50.')


class RecipeSchema(Schema):

    class Meta:
        ordered = True

    # Define our Recipe Schema to Validate/Serialize/Deserialize Object
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    ingredients = fields.String(validate=[validate.Length(max=1000)])
    directions = fields.String(validate=[validate.Length(max=1000)])
    cover_url = fields.Method(serialize='dump_cover_url')
    is_publish = fields.Boolean(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email', ))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('cook_time')
    def validate_cook_time(self, value):
        """This method has the logic to validate the 'cook_time' attribute"""
        if value < 1:
            raise ValidationError('Cook time must be greater than 0.')
        if value > 300:
            raise ValidationError('Cook time must not be greater than 300.')

    def dump_cover_url(self, recipe):
        """This method has got the logic to verify the cover image of the recipe."""
        if recipe.cover_image:
            return url_for('static', filename='images/recipes/{}'.format(recipe.cover_image), _external=True)
        else:  # set default cover image
            return url_for('static', filename='images/assets/default-recipe-cover.jpg', _external=True)


class RecipePaginationSchema(PaginationSchema):

    # Getting the source data of the 'items' to be attributed in the paging objects.
    data = fields.Nested(RecipeSchema, attribute='items', many=True)