import psycopg2
import os
from dotenv import load_dotenv


class Config:
    """Set Flask configuration vars from .env file."""

    load_dotenv()

    # General
    # TESTING = os.environ.get("TESTING")
    # FLASK_DEBUG = os.environ.get("FLASK_DEBUG")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') #'sqlite:///database.db' #
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SECRET_KEY = os.environ.get('SECRET_KEY')
