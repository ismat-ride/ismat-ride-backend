from functools import wraps
from flask_login import login_required
from src.rides.dto.ride_list_dto import RideListDto
from src.rides.rides import Ride
from flask import render_template, redirect, url_for, request
from flask_login import current_user
from src.rides import rides_bp

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.type != 'Student':
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@rides_bp.route("list")
@login_required
@student_required
def get():
      db_rides = Ride.query.all()

      rides_list = list()

      for ride in db_rides:
            rides_list.append(
                  RideListDto(ride.driver.get_full_name(),ride.origin, ride.status.name, 
                  ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers)) 
      )

      return render_template("rides/index.html", rides = rides_list)
