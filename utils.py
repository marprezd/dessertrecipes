# utils.py file
from passlib.hash import pbkdf2_sha256


def hash_password(password):
    """function for hashing password"""
    return pbkdf2_sha256.hash(password)


def check_password(password, hashed):
    """function for user authentication"""
    return pbkdf2_sha256.verify(password, hashed)