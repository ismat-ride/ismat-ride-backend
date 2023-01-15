from src.users import users_bp
from src.users.users import User
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from src.extensions import db, mail, SECRET_KEY
from flask_login import login_required, current_user
from flask_mail import Message
from cryptography.fernet import Fernet
import base64

@users_bp.route("/register")
def register():
    return render_template("users/register.html")

@users_bp.route("/register", methods = ['POST'])
def register_post():
    is_valid = True
    email = request.form.get("email")
    password = request.form.get("password")
    password_confirmation = request.form.get('password_confirmation')
    phone_number = request.form.get("phone_number")
    username = request.form.get('username')
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    student_number = request.form.get("student_number")

    if not email.endswith("@mso365.ismat.pt") or email is None:
        flash('Email de aluno nao pertence ao ISMAT', 'validation_error')
        is_valid = False

    if password is "" or None:
        flash('Por favor introduza uma password', 'validation_error')
        is_valid = False

    if password != password_confirmation:
        flash('Passwords nao são iguais', 'validation_error')
        is_valid = False

    if phone_number is "" or None:
        flash('Por favor introduza um numero de telefone', 'validation_error')
        is_valid = False

    if first_name is "" or None:
        flash('Por favor introduza o/a seu primeiro nome', 'validation_error')
        is_valid = False

    if last_name is "" or None:
        flash('Por favor introduza o/a seu último nome', 'validation_error')
        is_valid = False

    if username is "" or None:
        flash('Por favor introduza o/a seu nome de utilizador/a', 'validation_error')
        is_valid = False

    if student_number is "" or None:
        flash('Por favor introduza o/a seu número de estudante', 'validation_error')
        is_valid = False

    if not is_valid:
        return redirect(url_for('users.register'))

    new_user = User.query.filter_by(email=email).first()

    if new_user:
        flash('Já existe um utilizador com este email', 'already_exists_error')
        return redirect(url_for('users.register'))

    new_user = User(email=email, password=generate_password_hash(password), status="Pending", username=username, first_name=first_name, last_name=last_name, student_number=student_number, phone_number=phone_number, type="Student")

    db.session.add(new_user)
    db.session.commit()

    confirm_account_token = generate_password_hash(new_user.email)

    print(confirm_account_token)

    confirm_account_uri = f'{request.root_url}auth/confirm-account?token={confirm_account_token}'

    msg = Message('Bem-vindo!', sender = 'noreply@ismatride.com', recipients = [new_user.email])
    msg.html = render_template('email/confirm_account.html', first_name = new_user.first_name, confirm_account_url = confirm_account_uri)
    msg.body = render_template('email/confirm_account.html', first_name = new_user.first_name, confirm_account_url = confirm_account_uri)
    mail.send(msg)

    return render_template('users/created_account.html')

@users_bp.route('profile')
@login_required
def profile():
    return f'<h1> Hello {current_user.email}<h1>'