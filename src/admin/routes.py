import secrets
import string
from src.admin import admin_bp
from flask import render_template, flash, request, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_required
from src.users.users import Brand, Vehicle, Model
from src.rides.rides import Ride
from src.users.users import User
from src.admin.dto.user_list_dto import UserListDto
from src.admin.dto.ride_list_dto import RideListDto
from src.admin.dto.ride_requests_dto import RideRequestDto
from src.ride_requests.ride_requests import RideRequest
from src.extensions import db, mail, ITEMS_PER_PAGE
from flask_mail import Message

@admin_bp.route('/users/list', methods = [ 'GET' ])
def list_users():
    page = request.args.get('page', 1, type=int)

    users = User.query.filter_by(type = 'student').paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': users.iter_pages, 'page': page, 'pages': users.pages, 'next_num': users.next_num}

    user_list_dto = list()

    for user in users:
        print(user.status)
        user_list_dto.append(
            UserListDto(user.email, f'{user.first_name} {user.last_name}', user.phone_number, "teste", user.status, user.get_initials()) 
        )

    response['items'] = user_list_dto

    if user_list_dto.__len__() == 0:
        return(render_template("no_data/index.html"))

    return render_template('admin/users.html', user_list=response)

@admin_bp.route('send/recovery/<id>')
@login_required
def send_recovery(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('admin.users.get', id=id))

    new_password = ''.join((secrets.choice(string.ascii_letters) for i in range(8)))

    user.password = generate_password_hash(new_password)

    db.session.commit()

    msg = Message('Reset de pasword', sender = 'noreply@ismatride.com', recipients = [user.email])
    msg.html = render_template('email/recover_account.html', password = new_password)
    msg.body = render_template('email/recover_account.html', password = new_password)
    mail.send(msg)

    flash('Email de recuperação enviado', category='info')

    return redirect(request.url)

@admin_bp.route("/brands/list")
@login_required
def list_brands():
       page = request.args.get('page', 1, type=int)

       db_brands = Brand.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
       
       response = {'items': list(), 'iter_pages': db_brands.iter_pages, 'page': page, 'pages': db_brands.pages, 'next_num': db_brands.next_num}

       response['items'] = db_brands

       if not response['items'] :
        return(render_template("no_data/index.html"))

       return render_template("brands/index.html", brands = response)

@admin_bp.route("/brand/<id>", methods = ["POST"])
@login_required
def update_brand(id):
       brand = Brand.query.get(id)

       if(brand is None):
              flash('Esta marca nao existe', 'error')
              return redirect(url_for('admin.list_brands'))

       request_data = request.form.get("name")

       if(request_data is None):
              flash('Nome da marca nao pode vir vazio: ${name}', 'error')
              return redirect(url_for('admin.list_brands'))

       if(request_data == brand.name):
              flash('Esta marca já existe', 'error')
              return redirect(url_for('admin.list_brands'))

       brand.name = request_data

       try:
              db.session.commit()
              flash("MARCA ATUALIZADA COM SUCESSO!", 'info')
              return redirect(url_for('admin.list_brands'))
       except Exception as e:
              print(e)
              flash(f'Ocorreu um erro inesperado', 'error')

@admin_bp.route('/brand/delete/<brand_id>')
@login_required
def delete_brand(brand_id):
    brand_to_delete = Brand.query.filter_by(id=brand_id).first()

    if brand_to_delete is None:
        flash('Esta marca nao existe', category='not_found_error')
        
        return redirect(request.url)

    vehicles = db.session.query(Vehicle).filter(Vehicle.model.has(Model.brand_id == brand_id))

    if vehicles is None:
        db.session.remove(brand_to_delete)
        db.session.commit()

        return redirect(request.url)

    flash('Marca está a ser utilizada, não pode ser apagada', category='error')
    return redirect(request.url)

@admin_bp.route("/ride-requests/list")
@login_required
def list_ride_requests():
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
      
      if ride_requests_list.__len__() == 0:
        return(render_template("no_data/index.html"))

      return render_template("ride_requests/index.html", request_list = response)

@admin_bp.route("/models/list")
@login_required
def list_models():
    page = request.args.get('page', 1, type=int)

    db_models = Model.query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': db_models.iter_pages, 'page': page, 'pages': db_models.pages, 'next_num': db_models.next_num}

    response['items'] = db_models

    if not response['items']:
        return(render_template("no_data/index.html"))

    return render_template("models/index.html", request_list = response)

@admin_bp.route("rides/list")
@login_required
def list_rides():
    page = request.args.get('page', 1, type=int)
     
    db_rides = Ride.query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': db_rides.iter_pages, 'page': page, 'pages': db_rides.pages, 'next_num': db_rides.next_num}

    rides_list = list()
    
    for ride in db_rides:
        rides_list.append(
            RideListDto(ride.driver.get_full_name(),ride.local, ride.status.name, 
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers)) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("no_data/index.html"))

    return render_template("rides/index.html", request_list = response)    