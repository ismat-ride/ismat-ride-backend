from flask import Flask
from .extensions import db

DB_NAME = "rides.db"

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.secret_key="supersecretkey"

    #register blueprints
    from src.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
