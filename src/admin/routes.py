import secrets
import string
from src.admin import admin_bp
from flask import render_template, flash, request, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user, logout_user
from src.users.users import User
from src.admin.dto.user_list_dto import UserListDto
from src.users.users import Brand, Vehicle, Model
from src.extensions import db, mail, ITEMS_PER_PAGE
from flask_mail import Message

@admin_bp.route('/users/list', methods = [ 'GET' ])
@login_required
def list_users():
    page = request.args.get('page', 1, type=int)

    users = User.query.filter_by(type = 'student').paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': users.iter_pages, 'page': page, 'pages': users.pages, 'next_num': users.next_num}

    user_list_dto = list()

    for user in users:
        print(user.status)
        user_list_dto.append(
            UserListDto(user.email, f'{user.first_name} {user.last_name}', user.phone_number, "teste", user.status, user.get_initials()) 
        )

    response['items'] = user_list_dto

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

@admin_bp.route('login')
def login():
    if current_user.is_authenticated:
         return redirect(url_for('rides.get'))

    return render_template('admin/login.html')

@admin_bp.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    user = User.query.filter_by(email=email).first()
    if not user or user.type != 'admin' or not check_password_hash(user.password, password):
        flash('Credenciais invalidas', 'invalid_credentials')

        return render_template('admin/login.html')  

    response = make_response(redirect('login'))
    login_user(user)

    if remember_me:
        response.set_cookie('email', email, max_age=2880)
        response.set_cookie('password', password, max_age=2880)
        response.set_cookie('remember_me', remember_me, max_age=2880)
        response.set_cookie('admin', user.type, max_age=2880)

        return response

    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')
    response.delete_cookie('admin')

    return response

@admin_bp.route('/logout')
def logout():
    logout_user()
    response = make_response(redirect('login'))
    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')
    response.delete_cookie('admin')

    return response

@admin_bp.route('/edit/<id>', methods=['GET'])
@login_required
def edit_user(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('admin.list_users'))

    return render_template('admin/edit.html', user=user)


@admin_bp.route('/edit/<id>', methods=['POST'])
@login_required
def edit_user_post(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('admin.list_users'))
        
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.email = request.form.get('email')
    user.phone_number = request.form.get('phone_number')

    db.session.commit()

    flash('Utilizador editado com sucesso', category='info')

    return redirect(url_for('admin.edit_user', id=id))
