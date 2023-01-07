from src.rides.dto.ride_list_dto import RideListDto
from src.rides.rides import Ride
from flask import render_template
from src.rides import rides_bp


@rides_bp.route("get")
def get():
       rides = Ride.query.all()
       rides_list = list()

       for ride in rides:
               rides_list.append(
                     RideListDto(ride.user.get_full_name(),ride.local, ride.status, 
                     ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats) 
        )

       return render_template("rides/index.html", rides = rides_list)