from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_mail import Mail

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