from flask_login import login_required
from src.rides.dto.ride_list_dto import RideListDto
from src.rides.rides import Ride
from flask import render_template
from src.rides import rides_bp


@rides_bp.route("get")
@login_required
def get():
       db_rides = Ride.query.all()

       rides_list = list()

       for ride in db_rides:
               rides_list.append(
                     RideListDto(ride.driver.get_full_name(),ride.local, ride.status.name, 
                     ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers)) 
        )

       return render_template("rides/index.html", rides = rides_list)