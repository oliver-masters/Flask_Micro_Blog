import os
from pathlib import Path


basedir = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    db_path = basedir / 'app.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + str(db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
