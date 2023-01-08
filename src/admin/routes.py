from src.admin import admin_bp
from flask import render_template, flash, request, redirect
from flask_login import login_required
from src.users.users import User
from src.admin.dto.user_list_dto import UserListDto
from src.users.users import Brand, Vehicle, Model
from src.extensions import db

@admin_bp.route('/users/list', methods = [ 'GET' ])
def list_users():
    users = User.query.filter_by(type='student').all()

    print(users)

    response = list()

    for user in users:
        print(user.status)
        response.append(
            UserListDto(user.email, f'{user.first_name} {user.last_name}', user.phone_number, "teste", user.status, user.get_initials()) 
        )

    return render_template('admin/users.html', user_list=response)

@admin_bp.route('brands/delete/<brand_id>')
@login_required
def delete_brand(brand_id):
    brand_to_delete = Brand.query.filter_by(id=brand_id).first()

    if brand_to_delete is None:
        flash('Esta marca nao existe', category='not_found_error')
        
        return redirect(request.url)

    vehicles = db.session.query(Vehicle).filter(Vehicle.model.has(Model.brand_id == brand_id))

    if vehicles is None:
        db.session.remove(brand_to_delete)
        db.session.commit()

        return redirect(request.url)

    flash('Marca está a ser utilizada, não pode ser apagada', category='error')
    return redirect(request.url)