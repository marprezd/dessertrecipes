# utils.py file

# Import the necessary package and module
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

import os
import uuid
from PIL import Image

from flask_uploads import extension
from extensions import image_set, cache


def hash_password(password):
    """Function for hashing password"""
    return pbkdf2_sha256.hash(password)


def check_password(password, hashed):
    """Function for user authentication"""
    return pbkdf2_sha256.verify(password, hashed)


def generate_token(email, salt=None):
    """Function to create a token via email"""
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=salt)


def verify_token(token, max_age=(30 * 60), salt=None):
    """Function to extract the email address from the token."""
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))

    try:
        email = serializer.loads(token, max_age=max_age, salt=salt)
    except:
        return False

    return email


def save_image(image, folder):
    """Function to generate the filename for the uploaded image"""
    filename = '{}.{}'.format(uuid.uuid4(), extension(image.filename))
    image_set.save(image, folder=folder, name=filename)

    # We invoke the compress_image function and then it's stored within the
    # filename variable
    filename = compress_image(filename=filename, folder=folder)

    return filename


def compress_image(filename, folder):
    """Function to compress image"""
    file_path = image_set.path(filename=filename, folder=folder)

    # Create the image object from the image file.
    image = Image.open(file_path)

    # Check the color mode of the image and then convert the image
    # to the 'RGB' color mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize image; no bigger than 800 px
    if max(image.width, image.height) > 800:
        maxsize = (800, 800)
        image.thumbnail(maxsize, Image.ANTIALIAS)

    # Generate a new filename for our compressed image
    compressed_filename = '{}.jpg'.format(uuid.uuid4())

    # Also, generate the new path
    compressed_file_path = image_set.path(filename=compressed_filename, folder=folder)

    # Save image with quality = 85
    image.save(compressed_file_path, optimize=True, quality=85)

    # Get the size in bytes
    original_size = os.stat(file_path).st_size
    compressed_size = os.stat(compressed_file_path).st_size
    percentage = round((original_size - compressed_size) / original_size * 100)

    print(f'The file size is reduced by {percentage}%, from {original_size} to {compressed_size}')

    # Remove original image, return the compressed image
    os.remove(file_path)
    return compressed_filename


def clear_cache(key_prefix):
    """Function to clear the cache with a specific prefix"""
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)