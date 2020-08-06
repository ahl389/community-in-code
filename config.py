import psycopg2
import os
from dotenv import load_dotenv


class Config:
    """Set Flask configuration vars from .env file."""

    load_dotenv()

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    SECRET_KEY = os.environ.get('SECRET_KEY')
