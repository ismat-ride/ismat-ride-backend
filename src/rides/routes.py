from operator import or_
from sqlalchemy import func
from flask_login import login_required
from src.rides.dto.ride_list_dto import RideListDto
from src.rides.rides import Ride
from src.users.users import User
from flask import render_template, request
from src.rides import rides_bp
from src.extensions import student_required, ITEMS_PER_PAGE

@rides_bp.route("list")
@login_required
@student_required
def get():
    page = request.args.get('page', 1, type=int)

    query = Ride.query

    if request.args.get("name"):
        query = query.filter(or_(
            User.first_name.contains(request.args.get("name")),
            User.last_name.contains(request.args.get("name"))
            ))
    if request.args.get("origin"):
        query = query.filter(or_(Ride.origin.contains(request.args.get("origin")),
        Ride.destiny.contains(request.args.get("origin"))))
    if request.args.get("date"):
        query = query.filter(func.date(Ride.createdAt) == request.args.get("date"))
    if request.args.get("status"):
        query = query.filter(Ride.status_id == request.args.get("status"))

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    rides_list = list()
    
    for ride in query:
        rides_list.append(
            RideListDto(ride.driver.get_full_name(),ride.origin, ride.status.name, 
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers)) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("rides/no_data.html"))

    return render_template("rides/index.html", request_list = response)
