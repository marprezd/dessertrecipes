# main.py file

# Import the necessary package and module
from app import create_app

# This will be executed by Gunicorn to start up our web application
app = create_app()
