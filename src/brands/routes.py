from flask import redirect, render_template, request, url_for, flash
from flask_login import login_required
from src.brands import brand_bp
from src.users.users import Brand
from src.extensions import db

@brand_bp.route("get")
@login_required
def get():
       db_brands = Brand.query.all()
       return render_template("brands/index.html", brands = db_brands)

@brand_bp.route("edit/<id>", methods = ["POST"])
@login_required  
def update(id):
       brand = Brand.query.get(id)

       if(brand is None):
              flash('MARCA INVALIDA TENTE OUTRA VEZ!', 'error')
              return redirect(url_for('brand.get'))

       request_data = request.form.get("name")

       if(request_data is None):
              flash('ATRIBUTO INVALIDO, TEM QUE SER: ${name}', 'error')
              return redirect(url_for('brand.get'))

       if(request_data == brand.name):
              flash('NOME DA MARCA TEEM QUE SER DIFERENTE', 'error')
              return redirect(url_for('brand.get'))

       brand.name = request_data

       try:
              db.session.commit()
              flash("MARCA ATUALIZADA COM SUCESSO!", 'info')
              return redirect(url_for('brand.get'))
       except Exception as e:
               flash(f'{e}', 'error')