from flask import Blueprint

models_bp = Blueprint('models', __name__)

from src.models import routes