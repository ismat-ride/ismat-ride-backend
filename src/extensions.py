from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import current_user
from flask import redirect, url_for, request

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
migrate = Migrate()

mail = Mail()

SECRET_KEY = "Q68D65NhhTF9qLzYrXcFy9SIg2wgUu3PfiXUDL26Cug=" 
SQLALCHEMY_TRACK_MODIFICATIONS=False

ITEMS_PER_PAGE = 6

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.type != 'Student':
            return redirect(url_for('admin.list_users'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.type != 'Admin':
            return redirect(url_for('rides.list_rides'))
        return f(*args, **kwargs)
    return decorated_function