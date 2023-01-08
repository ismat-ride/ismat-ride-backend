from src.auth import auth_bp
from flask import render_template, redirect, request, flash, make_response
from flask_login import login_required, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from src.users.users import User


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    print(generate_password_hash(password))

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Credenciais invalidas', 'invalid_credentials')
        return render_template('auth/login.html')  

    response = make_response(redirect('login'))
    login_user(user)

    if remember_me:
        response.set_cookie('email', email, max_age=2880)
        response.set_cookie('password', password, max_age=2880)
        response.set_cookie('remember_me', remember_me, max_age=2880)

        return response

    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')

    return response