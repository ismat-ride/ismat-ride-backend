from src.extensions import db
import datetime

ride_passengers = db.Table('ride_passengers',
                    db.Column('passenger_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('ride_id', db.Integer, db.ForeignKey('ride.id'))
                    )

class Ride(db.Model):
    __tablename__ = 'ride' 
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    driver_id = db.Column('driver_id', db.ForeignKey('user.id')) 
    driver = db.relationship('User', backref='ride')
    passengers = db.relationship('User', secondary=ride_passengers, backref='ride')
    vehicle_id = db.Column('vehicle_id', db.ForeignKey('vehicle.id'))
    vehicle = db.relationship('Vehicle', backref='ride')
    local_id = db.Column('local_id', db.ForeignKey('local.id'))
    local = db.relationship('Local', backref='ride')
    seats = db.Column(db.Integer())
    cost = db.Column(db.Float, default=0.0)
    is_return_trip = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime, default=datetime.datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.datetime.now)
    status_id = db.Column('status_id', db.ForeignKey('ride_status.id'))
    status = db.relationship('RideStatus', backref='ride_status')

class RideStatus(db.Model):
    __tablename__ = 'ride_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Local(db.Model):
	__tablename__ = 'local'
	id =  db.Column(db.Integer, primary_key=True)
	user_id = db.Column('user_id', db.ForeignKey('user.id')) 
	user = db.relationship('User', backref='local')
	name = db.Column(db.String(100))
	description = db.Column(db.String(150))
	postal_code = db.Column(db.String(20))
	latitude = db.Column(db.Float)
	longitude = db.Column(db.Float)
	createdAt = db.Column(db.DateTime, default=datetime.datetime.now)
	updatedAt = db.Column(db.DateTime, default=datetime.datetime.now)