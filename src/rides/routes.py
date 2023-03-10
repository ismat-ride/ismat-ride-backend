import datetime
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
from datetime import timedelta

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

    time_format = "%Y-%d-%m %H:%M"

    currentTime = datetime.datetime.strptime(datetime.datetime.now().strftime(time_format), time_format)
    
    for ride in query:
        is_joinable = bool(RideRequest.query.filter(RideRequest.user_id == current_user.id).filter(RideRequest.ride_id == ride.id).filter(RideRequest.ride_request_state_id == 2).first())
        
        rides_list.append(
            RideListDto(str(ride.id), ride.driver.get_full_name(), ride.driver.get_initials(),ride.origin, ride.destiny, ride.status.name, 
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers),
            is_ride_joinable(currentTime, 
            datetime.datetime.strptime(ride.start_time.strftime(time_format), time_format),
            ride.status.name, is_joinable),ride.start_time ) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("rides/no_data.html"))

    return render_template("rides/index.html", request_list = response)

@rides_bp.route("my-rides/list")
@login_required
@student_required
def list_my_rides():
    page = request.args.get('page', 1, type=int)

    query = Ride.query.filter(Ride.driver_id == current_user.id)

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
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers), is_joinable, ride.start_time) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("rides/no_data.html"))

    return render_template("rides/my_rides.html", request_list = response)

@rides_bp.route('<id>', methods = [ 'GET' ])
@login_required
@student_required
def get_ride(id):
    ride = Ride.query.filter_by(id=id).first()

    time_format = "%Y-%d-%m %H:%M:%S"

    currentTime = datetime.datetime.strptime(datetime.datetime.now().strftime(time_format), time_format)

    if ride:
        passengers = list()
        is_joinable = bool(RideRequest.query.filter(RideRequest.user_id == current_user.id).filter(RideRequest.ride_id == ride.id).filter(RideRequest.ride_request_state_id == 2).first())

        for passenger in ride.passengers:
            passengers.append(PassengerListDto(passenger.id, passenger.get_initials(), passenger.first_name,
            passenger.last_name, passenger.username, passenger.phone_number, passenger.email,
            passenger.student_number))

        response = RideDto(str(ride.id), ride.origin, ride.destiny,
            ride.start_time, ride.vehicle.model.name, ride.vehicle.model.brand.name, ride.vehicle.license_plate,
            ride.vehicle.color, ride.seats, passengers,  is_ride_joinable(currentTime, 
            datetime.datetime.strptime(ride.start_time.strftime(time_format), time_format),
            ride.status.name, is_joinable))

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
        return redirect(request.referrer)
    
    if vehicle_id is None or vehicle_id is '':
        flash('A boleia tem que ter um ve??culo associado', category='error')
        is_valid = False
        return redirect(request.referrer)

    if total_seats is None or total_seats is '':
        flash('Uma boleia tem que ter no minimo 1 lugar dispon??vel', category='error')
        is_valid = False
        return redirect(request.referrer)

    if date is None or date is '':
        flash('Uma boleia tem que ter uma data associada', category='error')
        is_valid = False
        return redirect(request.referrer)

    if is_less_than_30_minutes(datetime.datetime.utcnow(), datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M')):
        flash('Uma boleia nao pode acontecer em menos de 30 Minutos', category='error')
        is_valid = False
        return redirect(request.referrer)

    if not is_valid:
        return redirect(request.referrer)

    ride_pending_status = RideStatus.query.filter_by(name='Activa').first()

    new_ride = Ride(
        start_time=datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M'),
        driver_id=driver,
        vehicle_id=vehicle_id,
        origin=origin,
        destiny=destiny,
        seats=total_seats,
        status=ride_pending_status)

    db.session.add(new_ride)
    db.session.commit()

    flash('Boleia criada com sucesso!', category='info')
    return redirect(request.referrer)

@login_required
@student_required
@rides_bp.route('/my-rides/edit/<id>', methods=['GET', 'POST'])
def edit_ride(id):
    
    ride = Ride.query.filter_by(id=id).first()

    ride.origin = request.form.get('origin')
    ride.destiny = request.form.get('destiny')
    ride.vehicle_id = request.form.get('vehicle')
    ride.seats = request.form.get('seats')
    ride.date = request.form.get('date')

    ride.start_time = datetime.datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M') 

    is_valid = True

    if ride.origin is '' or ride.destiny is '':
        flash('A boleia tem que ter um/a destino/origem', category='error')
        is_valid = False
        return redirect(url_for('rides.list_my_rides'))

    if ride.vehicle_id is None or ride.vehicle_id is '':
        flash('A boleia tem que ter um ve??culo associado', category='error')
        is_valid = False
        return redirect(url_for('rides.list_my_rides'))    

    if ride.seats is None or ride.seats is '':
        flash('Uma boleia tem que ter no minimo 1 lugar dispon??vel', category='error')
        is_valid = False
        return redirect(url_for('rides.list_my_rides'))

    if ride.start_time is None or ride.start_time is '':
        flash('Uma boleia tem que ter uma data associada', category='error')
        is_valid = False
        return redirect(url_for('rides.list_my_rides'))

    if not is_valid:
        return redirect(url_for('rides.list_my_rides'))  

    db.session.commit()

    flash('Boleia editada com sucesso', category='info')

    return redirect(url_for('rides.list_my_rides'))

@login_required
@student_required
@rides_bp.route('/my-rides/finish/<id>', methods=['GET', 'POST'])
def finish_ride(id):
    
    ride = Ride.query.filter_by(id=id).first()  
    ride.date = request.form.get('date')    

    print(ride.status_id)

    if ride.status_id == 2 :
        ride.status_id = 3 
        db.session.commit()
        flash('Boleia finalizada com sucesso', category='info')

    elif ride.status_id == 3 :
        flash('Esta boleia j?? est?? finalizada.', category='error')

    elif ride.status_id == 4 :
        flash('Esta boleia j?? est?? cancelada.', category='error')

    elif ride.status_id == 1 :
        flash('S?? ?? poss??vel finalizar boleias que j?? tenham come??ado.', category='error')

    return redirect(url_for('rides.list_my_rides'))

@login_required
@student_required
@rides_bp.route('/my-rides/cancel/<id>', methods=['GET', 'POST'])
def cancel_ride(id):
    
    ride = Ride.query.filter_by(id=id).first()

    time_format = "%Y-%d-%m %H:%M:%S"

    currentTime = datetime.datetime.strptime(datetime.datetime.now().strftime(time_format), time_format) 

    if ride.status_id == 4 :
        flash('Esta boleia j?? est?? cancelada.', category='error')

    else:
        if is_less_than_5_minutes(currentTime, datetime.datetime.strptime(ride.start_time.strftime(time_format), time_format)):
            flash('Uma boleia n??o pode ser cancelada a 5 minutos de come??ar', category='error')            
            return redirect(url_for('rides.list_my_rides'))
        else:  
            ride.status_id = 4 
            db.session.commit()
            flash('Boleia cancelada com sucesso', category='info')

    return redirect(url_for('rides.list_my_rides'))


@login_required
@student_required
@rides_bp.route('<id>/join', methods = [ 'POST' ])
def join_ride(id):
    ride_to_join = Ride.query.filter_by(id=id).first()

    if ride_to_join:
        initial_ride_request_state = RideRequestState.query.filter_by(name='Pendente').first()

        request_to_delete = RideRequest.query.filter_by(ride_id = ride_to_join.id).one()

        db.session.delete(request_to_delete)
        db.session.commit()

        ride_to_join_request = RideRequest(
            user=current_user,
            ride=ride_to_join,
            ride_request_state=initial_ride_request_state)

        db.session.add(ride_to_join_request)
        db.session.commit()

        flash('Pedido de boleia foi enviado para o condutor, podes verificar o estado na aba pedidos de boleia', category='info')
        return redirect(url_for('rides.list_rides'))

    flash('Error while entering ride, try again later', category='error')
    return redirect(url_for('rides.list_rides'))

def is_less_than_30_minutes(currentTime, rideTime):
    time_dif = (rideTime - currentTime) // timedelta(minutes=1)

    return time_dif < 30

def is_less_than_5_minutes(currentTime, rideTime):
    time_dif = (rideTime - currentTime) // timedelta(minutes=1)

    return time_dif < 5

def is_ride_joinable(currentTime, rideTime, rideStatus, is_joinable):
    time_dif = (rideTime - currentTime) // timedelta(minutes=1)
    if rideStatus == "Activa":
        if time_dif > 30 and is_joinable is False:
            return 'True'
        return 'False'
    return 'False'