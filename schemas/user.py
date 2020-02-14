# schemas/user.py file
from marshmallow import Schema, fields
from utils import hash_password


class UserSchema(Schema):
    class Meta:
        ordered = True

    # attributes we will receive in the client request
    id = fields.Int(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Method(required=True, deserialize='load_password')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


def load_password(value):
    """this function will be invoked when using load() deserialization"""
    return hash_password(value)
