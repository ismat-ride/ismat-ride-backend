from flask import Blueprint

ride_requests_bp = Blueprint('ride_requests', __name__)

from src.ride_requests import routes