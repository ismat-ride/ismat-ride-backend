from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()

SECRET_KEY = "SuperSecretKey" 
SQLALCHEMY_TRACK_MODIFICATIONS=False