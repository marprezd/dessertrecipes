# schemas/user.py file

# Import the necessary package and module
from flask import url_for
from marshmallow import Schema, fields
from utils import hash_password


class UserSchema(Schema):

    class Meta:
        ordered = True

    # Define our User Schema to Serialize/Deserialize Object
    id = fields.Int(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    avatar_url = fields.Method(serialize='dump_avatar_url')
    password = fields.Method(required=True, deserialize='load_password')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def load_password(self, value):
        """This method will be invoked when using load() deserialization"""
        return hash_password(value)

    def dump_avatar_url(self, user):
        """This method has got the logic to verify the avatar image of the user."""
        if user.avatar_image:
            return url_for(
                'static',
                filename=f'images/avatars/{user.avatar_image}',
                _external=True)
        else:  # set default avatar
            return url_for(
                'static',
                filename='images/assets/default-avatar.jpg',
                _external=True)