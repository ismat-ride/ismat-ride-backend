from src.users import users_bp
from src.users.users import User
from flask import render_template, request, redirect, url_for, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db
from flask_login import login_required, current_user

@users_bp.route("/register")
def register():
    return render_template("users/register.html")

@users_bp.route("/register", methods = ['POST'])
def register_post():
    is_valid = True
    email = request.form.get("email")
    password = request.form.get("password_confirmation")
    phone_number = request.form.get("phone_number")
    first_name = request.form.get("first_name")

    if not email.endswith("@mso365.ismat.pt") or email is None:
        flash('Email de aluno nao pertence ao ISMAT', 'validation_error')
        is_valid = False
    
    print(password)

    if password is "" or None:
        flash('Por favor introduza uma password', 'validation_error')
        is_valid = False

    if phone_number is "" or None:
        flash('Por favor introduza um numero de telefone', 'validation_error')
        is_valid = False

    if first_name is "" or None:
        flash('Por favor introduza o/a seu primeiro nome', 'validation_error')
        is_valid = False

    if not is_valid:
        return redirect(url_for('users.register'))

    new_user = User.query.filter_by(email=email).first()

    if new_user:
        flash('Já existe um utilizador com este email', 'already_exists_error')
        return redirect(url_for('users.register'))

    new_user = User(email=email, password=generate_password_hash(password), status="Pending", first_name=first_name, last_name="dummy", student_number="dummy", phone_number=phone_number)

    db.session.add(new_user)
    db.session.commit()

    return f"<h1>Welcome {new_user.email} to ISMATRIDE"

@users_bp.route('profile')
@login_required
def profile():
    return f'<h1> Hello {current_user.email}<h1>'