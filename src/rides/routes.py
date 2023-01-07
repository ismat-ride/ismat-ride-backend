from flask import render_template
from src.rides import rides_bp

@rides_bp.route("get")
def get():
       return render_template("rides/index.html", rides=[a])