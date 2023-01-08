import secrets
import string
from src.admin import admin_bp
from flask import render_template, flash, request, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_required
from src.users.users import User
from src.admin.dto.user_list_dto import UserListDto
from src.users.users import Brand, Vehicle, Model
from src.extensions import db, mail
from flask_mail import Message

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

@admin_bp.route('send/recovery/<id>')
@login_required
def send_recovery(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('admin.users.get', id=id))

    new_password = ''.join((secrets.choice(string.ascii_letters) for i in range(8)))

    user.password = generate_password_hash(new_password)

    db.session.commit()

    msg = Message('Reset de pasword', sender = 'noreply@ismatride.com', recipients = [user.email])
    msg.html = render_template('email/recover_account.html', password = new_password)
    msg.body = render_template('email/recover_account.html', password = new_password)
    mail.send(msg)

    flash('Email de recuperação enviado', category='info')

    return redirect(request.url)