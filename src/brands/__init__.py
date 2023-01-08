from flask import Blueprint

brand_bp = Blueprint('brand', __name__)

from src.brands import routes