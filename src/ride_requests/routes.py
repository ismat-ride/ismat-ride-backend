from flask import render_template
from src.ride_requests import ride_requests_bp
from src.ride_requests.dto.ride_requests_dto import RideRequestDto
from .ride_requests import RideRequest

@ride_requests_bp.route("get")
def get():
       db_ride_requests = RideRequest.query.all()

       ride_requests_list = list()

       for ride in db_ride_requests:
               ride_requests_list.append(
                     RideRequestDto(ride.user.get_full_name(),ride.ride.driver.get_full_name(),ride.local.name, ride.ride_request_state.name, 
                     ride.ride.start_time.strftime('%d-%m-%Y'), ride.ride.start_time.strftime('%H:%M')) 
        )

       return render_template("ride_requests/index.html", request_list = ride_requests_list)