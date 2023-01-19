import datetime
from src.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.Unicode(80))
	username = db.Column(db.String(50))
	status = db.Column(db.String(20))
	first_name = db.Column(db.String(100))
	last_name = db.Column(db.String(100))
	student_number = db.Column(db.String(50))
	phone_number = db.Column(db.String(100))
	type = db.Column(db.String(20))
	
	def get_full_name(self):
		return self.first_name + " " + self.last_name	

	def get_initials(self):
		first_name_initial = str.upper(self.first_name[0])
		last_name_initial = str.upper(self.last_name[0])
		return f'{first_name_initial}{last_name_initial}'

class Brand(db.Model):
	__tablename__ = 'brand'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))

class Model(db.Model):
	__tablename__ = 'model'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	brand_id = db.Column('brand_id', db.ForeignKey('brand.id'))
	brand = db.relationship('Brand', backref='brand')

class Vehicle(db.Model):
	__tablename__ = 'vehicle'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column('user_id', db.ForeignKey('user.id')) 
	user = db.relationship('User', backref='vehicle')
	license_plate = db.Column(db.String(20), unique=True)
	color = db.Column(db.String(20))
	seats = db.Column(db.Integer, default=0)
	is_deleted = db.Column(db.Boolean, default=False)
	createdAt = db.Column(db.DateTime, default=datetime.datetime.now)
	updatedAt = db.Column(db.DateTime, default=datetime.datetime.now)
	model_id = db.Column('model_id', db.ForeignKey('model.id')) 
	model = db.relationship('Model', backref='vehicle')