from flask import render_template
from flask_login import login_required
from src.models import models_bp
from src.users.users import Model

@models_bp.route("get")
@login_required
def get():
    db_models = Model.query.all()
    return render_template("models/index.html", models = db_models)