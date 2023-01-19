
from flask import render_template, request
from flask_login import current_user, login_required
from src.extensions import ITEMS_PER_PAGE
from src.ride_requests.dto.my_requests_list_dto import MyRequestsListDto
from src.ride_requests.ride_requests import RideRequest
from src.ride_requests import ride_requests_bp

@ride_requests_bp.route("/list")
@login_required
def my_requests_list():
    page = request.args.get('page', 1, type=int)

    query = RideRequest.query.filter(RideRequest.user_id == current_user.id)

    """ if request.args.get("model"):
        query = query.join(Model, Vehicle.model).filter(Model.name.contains(request.args.get("model")))
    if request.args.get("brand"):
        query = query.join(Model, Vehicle.model).join(Brand, Model.brand).filter(Brand.name.contains(request.args.get("brand")))
    if request.args.get("vin"):
        query = query.filter(Vehicle.license_plate.contains(request.args.get("vin"))) """

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    my_requests_lid = list()
    
    for item in query:
        my_requests_lid.append(
            MyRequestsListDto(item.id, item.ride.origin, item.ride.destiny, item.ride_request_state.name,
            item.ride.start_time, item.ride.start_time, True) 
        )

    response['items'] = my_requests_lid

    if my_requests_lid.__len__() == 0:
        return(render_template("ride_requests/no_data.html"))

    return render_template("ride_requests/my_requests.html", request_list = response)    