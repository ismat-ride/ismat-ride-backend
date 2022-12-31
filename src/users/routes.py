from src.users import users_bp
from flask import render_template, request, redirect, url_for, jsonify
from .users import User
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db

@users_bp.route("/")
def test():
    return User.query.first().__str__()

@users_bp.route("/register")
def register():
    return render_template("users/register.html")

@users_bp.route("/register", methods= ['POST'])
def register_post():
    # email = request.form.get("email")
    # password = request.form.get("password")

    # new_user = User.query.filter_by(email=email).first()

    # if new_user:
    #     return redirect(url_for('users_bp.test'))

    new_user = User(email="dummy", password=generate_password_hash("testing"), status="Pending", first_name="dummy", last_name="dummy", student_number="dummy", phone_number="dummy")

    db.session.add(new_user)
    db.session.commit()

    return f"<h1>Welcome {new_user.email} to ISMATRIDE"