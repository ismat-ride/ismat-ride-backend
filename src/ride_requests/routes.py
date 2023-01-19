
import datetime
from datetime import timedelta
from operator import or_
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from src.extensions import db, ITEMS_PER_PAGE
from src.ride_requests.dto.my_requests_list_dto import MyRequestsListDto
from src.ride_requests.ride_requests import RideRequest
from src.ride_requests import ride_requests_bp
from src.rides.rides import Ride

@ride_requests_bp.route("/list")
@login_required
def my_requests_list():
    page = request.args.get('page', 1, type=int)

    query = RideRequest.query.filter(RideRequest.user_id == current_user.id)

    if request.args.get("origin"):
        query = query.join(Ride, RideRequest.ride).filter(or_(
            Ride.origin.contains(request.args.get("origin")),
            Ride.destiny.contains(request.args.get("origin"))
            ))
    if request.args.get("date"):
        query = query.filter(func.date(RideRequest.createdAt) == request.args.get("date"))
    if request.args.get("status"):
        query = query.filter(RideRequest.ride_request_state_id == request.args.get("status"))

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    my_requests_lid = list()

    time_format = "%Y-%d-%m %H:%M:%S"

    currentTime = datetime.datetime.strptime(datetime.datetime.now().strftime(time_format), time_format)

    for item in query:
        my_requests_lid.append(
            MyRequestsListDto(item.id, item.ride.origin, item.ride.destiny, item.ride_request_state.name,
            item.ride.start_time.strftime('%d-%m-%Y'), item.ride.start_time.strftime('%H:%M'), getIsCancalable(currentTime, 
            datetime.datetime.strptime(item.ride.start_time.strftime(time_format), time_format),
            item.ride_request_state.name)) 
        )

    response['items'] = my_requests_lid

    if my_requests_lid.__len__() == 0:
        return(render_template("ride_requests/my_requests_no_data.html"))

    return render_template("ride_requests/my_requests.html", request_list = response)    

def getIsCancalable(currentTime, rideTime, rideStatus):

    time_dif = (rideTime - currentTime) // timedelta(minutes=1)

    if rideStatus == "ACEITE" or rideStatus == "PENDENTE":
        if time_dif > 30:
            return 'True'
        return 'False'
    return 'False'        

@ride_requests_bp.route("my-request/cancel_request/<id>", methods=["POST"])
@login_required
def cancel_request(id):
    ride_request = RideRequest.query.get(id)
    ride_request.ride_request_state_id = 4

    db.session.commit()
    flash("Pedido de boleia cancelado com sucesso!", "info")
    return redirect(url_for('ride_requests.my_requests_list'))