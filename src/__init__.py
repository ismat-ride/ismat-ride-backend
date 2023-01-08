from flask import Flask
from .extensions import db, migrate, mail, SECRET_KEY
from flask_mail import Mail
from .users.users import *
from .rides.rides import *
from flask_login import LoginManager
from .users.users import *
from .rides.rides import *
from .ride_requests import *

DB_NAME = "rides.db"

mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.secret_key=SECRET_KEY

    ##Email configs
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'ismatridenoreply@gmail.com'
    app.config['MAIL_PASSWORD'] = 'jrescxyosdilmhbh'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)

    #register blueprints
    from src.users import users_bp
    from src.auth import auth_bp
    from src.admin import admin_bp
    app.register_blueprint(users_bp, url_prefix = '/users')
    app.register_blueprint(auth_bp, url_prefix = '/auth')
    app.register_blueprint(admin_bp, url_prefix = '/admin')

    from src.rides import rides_bp
    app.register_blueprint(rides_bp, url_prefix = '/rides')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from src.users.users import User

    db.init_app(app)
    with app.app_context():
        db.create_all()
        migrate.init_app(app, db, render_as_batch=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
