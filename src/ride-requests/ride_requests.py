from extensions import db

class RideRequest(db.Model):
	__tablename__ = 'ride_request'
	__table_args__ = (db.UniqueConstraint('user_id', 'ride_id'),)
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	user = db.relationship('User', backref='ride_request')
	ride_id = db.Column('ride_id', db.ForeignKey('ride.id'))
	ride = db.relationship('Ride', backref='ride_request')
	local_id = db.Column('local_id', db.ForeignKey('local.id'))
	local = db.relationship('Local', backref='ride_request')
	ride_request_state_id = db.Column('ride_request_state_id', db.ForeignKey('ride_request_state.id'), default=1)
	ride_request_state = db.relationship('RideRequestState', backref='ride_request')
	createdAt = db.Column(db.DateTime, default=datetime.now)
	updatedAt = db.Column(db.DateTime, default=datetime.now)

class RideRequestState(db.Model):
   __tablename__ = 'ride_request_state'
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(20))