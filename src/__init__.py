from flask import Flask
from .extensions import db
from .users.users import *
from .rides.rides import *
from .ride_requests.ride_requests import *
from flask_login import LoginManager

DB_NAME = "rides.db"

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.secret_key="supersecretkey"

    #register blueprints
    from src.users import users_bp
    from src.auth import auth_bp
    from src.admin import admin_bp
    app.register_blueprint(users_bp, url_prefix = '/users')
    app.register_blueprint(auth_bp, url_prefix = '/auth')
    app.register_blueprint(admin_bp, url_prefix = '/admin')

    from src.rides import rides_bp
    app.register_blueprint(rides_bp, url_prefix = '/rides')

    from src.ride_requests import ride_requests_bp
    app.register_blueprint(ride_requests_bp, url_prefix = '/ride-requests')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from src.users.users import User

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app