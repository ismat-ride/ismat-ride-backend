from flask import redirect, render_template, request, url_for, flash
from flask_login import login_required
from src.brands import brand_bp
from src.users.users import Brand
from src.extensions import db, ITEMS_PER_PAGE

@brand_bp.route("get")
@login_required
def get():
       page = request.args.get('page', 1, type=int)

       db_brands = Brand.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
       
       response = {'items': list(), 'iter_pages': db_brands.iter_pages, 'page': page, 'pages': db_brands.pages, 'next_num': db_brands.next_num}

       response['items'] = db_brands

       return render_template("brands/index.html", brands = response)

@brand_bp.route("edit/<id>", methods = ["POST"])
@login_required
def update(id):
       brand = Brand.query.get(id)

       if(brand is None):
              flash('Esta marca nao existe', 'error')
              return redirect(url_for('brand.get'))

       request_data = request.form.get("name")

       if(request_data is None):
              flash('Nome da marca nao pode vir vazio: ${name}', 'error')
              return redirect(url_for('brand.get'))

       if(request_data == brand.name):
              flash('Esta marca já existe', 'error')
              return redirect(url_for('brand.get'))

       brand.name = request_data

       try:
              db.session.commit()
              flash("MARCA ATUALIZADA COM SUCESSO!", 'info')
              return redirect(url_for('brand.get'))
       except Exception as e:
              print(e)
              flash(f'Ocorreu um erro inesperado', 'error')