from flask import render_template, request
from flask_login import login_required
from src.ride_requests import ride_requests_bp
from src.ride_requests.dto.ride_requests_dto import RideRequestDto
from .ride_requests import RideRequest
from src.extensions import ITEMS_PER_PAGE

@ride_requests_bp.route("get")
@login_required
def get():
      page = request.args.get('page', 1, type=int)

      db_ride_requests = RideRequest.query.paginate(page=page, per_page=ITEMS_PER_PAGE)

      response = {'items': list(), 'iter_pages': db_ride_requests.iter_pages, 'page': page, 'pages': db_ride_requests.pages, 'next_num': db_ride_requests.next_num}

      ride_requests_list = list()

      for ride in db_ride_requests:
            ride_requests_list.append(
                  RideRequestDto(ride.user.get_full_name(),ride.ride.driver.get_full_name(),ride.local.name, ride.ride_request_state.name, 
                  ride.ride.start_time.strftime('%d-%m-%Y'), ride.ride.start_time.strftime('%H:%M')) 
            )

      response['items'] = ride_requests_list

      return render_template("ride_requests/index.html", request_list = response)