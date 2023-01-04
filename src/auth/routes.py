from src.auth import auth_bp
from flask import render_template, redirect, request, flash
from src.users.users import User


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or user.password is not password:
        flash('Credenciais invalidas', 'invalid_credentials')
        return render_template('auth/login.html')  

    return redirect("https://google.com") 