from flask import Flask
from .extensions import db
from .users.users import *
from .rides.rides import *

DB_NAME = "rides.db"

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.secret_key="supersecretkey"

    #register blueprints
    from src.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    #rides blueprints
    from src.rides import rides_bp
    app.register_blueprint(rides_bp, url_prefix='/rides')

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
