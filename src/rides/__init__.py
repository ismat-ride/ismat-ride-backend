from flask import Blueprint

rides_bp = Blueprint('rides', __name__)

from src.rides import routes