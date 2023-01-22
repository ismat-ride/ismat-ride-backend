import secrets
import string
from src.auth import auth_bp
from flask import render_template, redirect, request, flash, make_response, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from src.users.users import User
from src.extensions import mail, db
from flask_mail import Message

@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('rides.list_rides'))

    return render_template('auth/login.html')

@auth_bp.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    user = User.query.filter_by(email=email).first()

    if user.type != 'Student' or not check_password_hash(user.password, password):
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

@auth_bp.route('recover', methods = ['GET'])
def recover_get():
    return render_template('auth/recover.html')

@auth_bp.route('recover', methods = ['POST'])
def recover_post():
    user = User.query.filter_by(email=request.form.get('email')).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('auth.recover_get'))
    
    new_password = ''.join((secrets.choice(string.ascii_letters) for i in range(8)))

    user.password = generate_password_hash(new_password)

    db.session.commit()

    msg = Message('Reset de pasword', sender = 'noreply@ismatride.com', recipients = [user.email])
    msg.html = render_template('email/recover_account.html', password = new_password)
    msg.body = render_template('email/recover_account.html', password = new_password)
    mail.send(msg)

    flash('Email enviado com nova password', category='info')

    return render_template('auth/login.html')

@auth_bp.route('confirm-account', methods = [ 'GET' ])
def confirm_account():
    return render_template('auth/confirm_account.html')

@auth_bp.route('confirm-account', methods = [ 'POST' ])
def confirm_account_post():
    token = request.args.get('token')

    user_to_confirm = User.query.filter(User.status.like('Pending')).all()

    for user in user_to_confirm:
        if check_password_hash(token, user.email):
            user.status = 'Active'
            db.session.commit()

            return redirect(url_for('auth.login'))

    flash('Esta conta não existe', 'error')
    return render_template('auth/confirm_account.html')

@auth_bp.route('logout')
def logout():
    logout_user()
    response = make_response(redirect('login'))
    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')

    return response
