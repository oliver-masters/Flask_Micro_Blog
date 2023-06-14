from flask import Flask

# Create the Flask application
app = Flask(__name__)

from app import routes
