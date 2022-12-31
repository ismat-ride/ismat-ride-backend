from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

SECRET_KEY = "SuperSecretKey" 
SQLALCHEMY_TRACK_MODIFICATIONS=False