from operator import or_
from sqlalchemy import func
from flask_login import login_required
from src.rides.dto.ride_list_dto import RideListDto, RideDto, PassengerListDto
from src.rides.rides import Ride, RideStatus
from src.users.users import User
from src.ride_requests.ride_requests import RideRequest, RideRequestState
from flask import render_template, request, url_for, flash, redirect
from src.rides import rides_bp
from src.extensions import student_required, ITEMS_PER_PAGE, db
from flask_login import current_user
from datetime import datetime, timedelta

@rides_bp.route("list")
@login_required
@student_required
def list_rides():
    page = request.args.get('page', 1, type=int)

    query = Ride.query.filter(Ride.driver_id != current_user.id)

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
        is_joinable = RideRequest.query.filter_by(user_id=current_user.id, ride_id=ride.id) == None
   
        rides_list.append(
            RideListDto(str(ride.id), ride.driver.get_full_name(), ride.driver.get_initials(),ride.origin, ride.destiny, ride.status.name, 
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers), is_joinable) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("rides/no_data.html"))

    return render_template("rides/index.html", request_list = response)

@rides_bp.route('<id>', methods = [ 'GET' ])
@login_required
@student_required
def get_ride(id):
    ride = Ride.query.filter_by(id=id).first()

    if ride:
        passengers = list()
        is_joinable = RideRequest.query.filter_by(user_id=current_user.id, ride_id=ride.id) == None

        for passenger in ride.passengers:
            passengers.append(PassengerListDto(passenger.id, passenger.get_initials()))

        response = RideDto(str(ride.id), ride.origin, ride.destiny, ride.vehicle.model,
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, passengers, is_joinable)

        return render_template('rides/ride.html', ride = response)

    return url_for('rides.list_rides')

@login_required
@student_required
@rides_bp.route('create', methods = [ 'POST' ])
def create_ride():
    origin = request.form.get('origin')
    destiny = request.form.get('destiny')
    vehicle_id = request.form.get('vehicle')
    driver = current_user.id
    total_seats = request.form.get('seats')
    date = request.form.get('date')

    is_valid = True

    if origin is None or destiny is None:
        flash('A boleia tem que ter um/a destino/origem', category='error')
        is_valid = False
    
    if vehicle_id is None:
        flash('A boleia tem que ter um veículo associado', category='error')
        is_valid = False

    if total_seats is '':
        flash('Uma boleia tem que ter no minimo 1 lugar disponível', category='error')
        is_valid = False

    if date is '':
        flash('Uma boleia tem que ter uma data associada', category='error')
        is_valid = False

    if is_less_than_30_minutes(datetime.utcnow(), datetime.strptime(date, '%Y-%m-%dT%H:%M')):
        flash('Uma boleia nao pode acontecer em menos de 30 Minutos', category='error')
        is_valid = False

    if not is_valid:
        return redirect(request.referrer)

    ride_pending_status = RideStatus.query.filter_by(name='Activa').first()

    new_ride = Ride(
        start_time=datetime.strptime(date, '%Y-%m-%dT%H:%M'),
        driver_id=driver,
        vehicle_id=vehicle_id,
        origin=origin,
        destiny=destiny,
        seats=total_seats,
        status=ride_pending_status)

    db.session.add(new_ride)
    db.session.commit()

    flash('A sua boleia foi criada', category='info')

    return redirect(request.referrer)

@login_required
@student_required
@rides_bp.route('<id>/join', methods = [ 'POST' ])
def join_ride(id):
    ride_to_join = Ride.query.filter_by(id=id).first()

    if ride_to_join:
        initial_ride_request_state = RideRequestState.query.filter_by(name='Pendente').first()

        ride_to_join_request = RideRequest(
            user=current_user,
            ride=ride_to_join,
            ride_request_state=initial_ride_request_state)

        db.session.add(ride_to_join_request)
        db.session.commit()

        flash('Pedido de boleia foi enviado para o condutor, podes verificar o estado na aba pedidos de boleia', category='info')
        return render_template('rides/ride.html', ride = ride_to_join)

    flash('Error while entering ride, try again later', category='error')
    return url_for('rides.list_rides')

def is_less_than_30_minutes(currentTime, rideTime):
    time_dif = (rideTime - currentTime) // timedelta(minutes=1)

    return time_dif < 30