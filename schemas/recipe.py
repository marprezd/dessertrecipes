# schemas/recipe.py file
from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema


def validate_num_of_servings(number):
    """validate the 'num_of_servings' attribute. This is a customized validation function"""
    if number < 1:
        raise ValidationError('Number of servings must be greater than 0.')
    if number > 50:
        raise ValidationError('Number of servings must not be greater than 50.')


class RecipeSchema(Schema):
    class Meta:
        ordered = True

    # attributes to validate and serializing
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    directions = fields.String(validate=[validate.Length(max=1000)])
    is_publish = fields.Boolean(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # validate the 'cook_time' attribute. Another customized validation method using a decorator
    @validates('cook_time')
    def validate_cook_time(self, value):
        """the cooking time should be between 1 minute and 300 minutes"""
        if value < 1:
            raise ValidationError('Cook time must be greater than 0.')
        if value > 300:
            raise ValidationError('Cook time must not be greater than 300.')

    # finally, the processing can be done when the recipe is serialized
    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        """this method return only one recipe or many recipes"""
        if many:
            return {'data': data}
        return data
