from flask import render_template
from flask_login import login_required
from src.brands import brand_bp
from src.users.users import Brand

@brand_bp.route("get")
@login_required
def get():
       db_brands = Brand.query.all()
       return render_template("brands/index.html", brands = db_brands)