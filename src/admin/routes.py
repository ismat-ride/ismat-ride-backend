from operator import or_
import secrets
import string
from sqlalchemy import func
from src.admin import admin_bp
from flask import render_template, flash, request, redirect, url_for,make_response
from src.users.users import User, Brand, Vehicle, Model
from src.rides.rides import Local, Ride
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user, logout_user
from src.admin.dto.user_list_dto import UserListDto
from src.admin.dto.ride_list_dto import RideListDto
from src.admin.dto.ride_requests_dto import RideRequestDto
from src.ride_requests.ride_requests import RideRequest
from src.extensions import db, mail, ITEMS_PER_PAGE, admin_required
from flask_mail import Message


@admin_bp.route('/users/list', methods = [ 'GET' ])
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    
    query = User.query.filter(User.type == "Student")

    if request.args.get("name"):
        query = query.filter(or_(
            User.first_name.contains(request.args.get("name")),
            User.last_name.contains(request.args.get("name"))
            ))
    if request.args.get("email"):
        query = query.filter(
            User.email.contains(request.args.get("email")))
    if request.args.get("number"):
        query = query.filter(
            User.phone_number.contains(request.args.get("number")))
    if request.args.get("status"):
        query = query.filter(User.status == request.args.get("status"))

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    user_list_dto = list()

    for user in query:
        user_list_dto.append(
            UserListDto(user.id, user.get_full_name(), user.email, user.username, user.first_name, user.last_name, user.phone_number, "teste", user.status, user.get_initials()) 
        )

    response['items'] = user_list_dto

    if user_list_dto.__len__() == 0:
        return(render_template("admin/no_data.html"))

    return render_template('admin/users.html', user_list=response)

@admin_bp.route('send/recovery/<id>')
@login_required
@admin_required
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

    flash('Email de recupera????o enviado', category='info')

    return redirect(url_for('admin.list_users'))

@admin_bp.route("/brands/list")
@login_required
@admin_required
def list_brands():
       page = request.args.get('page', 1, type=int)
       
       query = Brand.query
       
       if request.args.get("brand"):
        query = query.filter(
            Brand.name.contains(request.args.get("brand")))
       
       query = query.paginate(page=page, per_page=ITEMS_PER_PAGE) 
       
       response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

       response['items'] = query

       if len(query.items) == 0 :
        return(render_template("brands/no_data.html"))

       return render_template("brands/index.html", brands = response)

@admin_bp.route("/brand/<id>", methods = ["POST"]) 
@login_required
@admin_required
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
              flash('Esta marca j?? existe', 'error')
              return redirect(url_for('admin.list_brands'))

       brand.name = request_data

       try:
              db.session.commit()
              flash("MARCA ATUALIZADA COM SUCESSO!", 'info')
              return redirect(url_for('admin.list_brands'))
       except Exception as e:
              print(e)
              flash(f'Ocorreu um erro inesperado', 'error')

@admin_bp.route('/brand/delete/<id>')
@login_required
@admin_required
def delete_brand(id):
    brand_to_delete = Brand.query.filter_by(id=id).first()

    if brand_to_delete is None:
        flash('Esta marca nao existe', category='not_found_error')
        
        return redirect(url_for('admin.list_brands'))

    if brand_to_delete is None:
        flash('Esta marca nao existe', category='not_found_error')
        return redirect(url_for('admin.list_brands'))
    

    try:
        db.session.delete(brand_to_delete)
        db.session.commit()
        flash("MARCA APAGADA COM SUCESSO!", 'info')
        return redirect(url_for('admin.list_brands'))
    except:
        flash(f'Ocorreu um erro inesperado', 'error')


@admin_bp.route("/ride-requests/list")
@login_required
@admin_required
def list_ride_requests():
      page = request.args.get('page', 1, type=int)

      query = RideRequest.query

      if request.args.get("name"):
        query = query.join(Ride, RideRequest.ride).join(User, Ride.driver).filter(or_(
            User.first_name.contains(request.args.get("name")),
            User.last_name.contains(request.args.get("name"))
            ))
      if request.args.get("origin"):
        query = query.join(Ride, RideRequest.ride).filter(
            Ride.origin.contains(request.args.get("origin")))
      if request.args.get("date"):
        query = query.filter(func.date(RideRequest.createdAt) == request.args.get("date"))
      if request.args.get("status"):
        query = query.filter(RideRequest.ride_request_state_id == request.args.get("status"))
        
      query = query.paginate(page=page, per_page=ITEMS_PER_PAGE) 

      response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

      ride_requests_list = list()

      for ride in query:
            ride_requests_list.append(
                  RideRequestDto(ride.user.get_full_name(),ride.ride.driver.get_full_name(),ride.ride.origin, ride.ride.destiny, ride.ride_request_state.name, 
                  ride.ride.start_time.strftime('%d-%m-%Y'), ride.ride.start_time.strftime('%H:%M'),ride.ride.driver.get_initials()) 
            )

      response['items'] = ride_requests_list
      
      if ride_requests_list.__len__() == 0:
        return(render_template("admin/ride_requests_no_data.html"))

      return render_template("admin/ride_requests.html", request_list = response)

@admin_bp.route("/models/list")
@login_required
@admin_required
def list_models():
    page = request.args.get('page', 1, type=int)

    query = Model.query
    modal_brand = Brand.query.all()      

    if request.args.get("brand"):
        query = query.filter(
            Brand.name.contains(request.args.get("brand")))
    if request.args.get("model"):
        query = query.filter(
            Model.name.contains(request.args.get("model")))

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE) 

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    response['items'] = query

    if len(query.items) == 0:
        return(render_template("models/no_data.html"))

    return render_template("models/index.html", request_list = response,  modal_brand_2 = modal_brand)

@admin_bp.route("rides/list")
@login_required
@admin_required
def list_rides():
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
            RideListDto(ride.driver.get_full_name(),ride.origin,ride.destiny, ride.status.name, 
            ride.start_time.strftime('%d-%m-%Y'), ride.start_time.strftime('%H:%M'), ride.seats, ride.seats - len(ride.passengers),ride.driver.get_initials()) 
        )

    response['items'] = rides_list

    if rides_list.__len__() == 0:
        return(render_template("admin/rides_no_data.html"))

    return render_template("admin/rides.html", request_list = response)    


@admin_bp.route('login')
def login():
    if current_user.is_authenticated:
         return redirect(url_for('admin.list_rides'))

    return render_template('admin/login.html')

@admin_bp.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    user = User.query.filter_by(email=email).first()
    
    if not user or user.type != 'Admin' or not check_password_hash(user.password, password):
        flash('Credenciais invalidas', 'invalid_credentials')

        return render_template('admin/login.html')  

    response = make_response(redirect('login'))
    login_user(user)

    if remember_me:
        response.set_cookie('email', email, max_age=2880)
        response.set_cookie('password', password, max_age=2880)
        response.set_cookie('remember_me', remember_me, max_age=2880)
        response.set_cookie('admin', user.type, max_age=2880)

        return response

    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')
    response.delete_cookie('admin')

    return response

@admin_bp.route('/logout')
def logout():
    logout_user()
    response = make_response(redirect('login'))
    response.delete_cookie('email')
    response.delete_cookie('password')
    response.delete_cookie('remember_me')
    response.delete_cookie('admin')

    return response

@admin_bp.route("/edit", methods=["POST"])
@login_required
@admin_required
def edit_user_post():
    new_user = current_user

    if request.form.get('firstname') == "" or request.form.get('firstname') is None:
        flash('Insira um primeiro nome!', 'error')
        return redirect(request.referrer)
    if request.form.get('lastname') == "" or request.form.get('lastname') is None:
        flash('Insira um ultimo nome!', 'error')
        return redirect(request.referrer)
    if request.form.get('email') == "" or request.form.get('email') is None:
        flash('Insira um email!', 'error')
        return redirect(request.referrer)
    if request.form.get('phone') == "" or request.form.get('phone') is None:
        flash('Insira um n??mero de telefone!', 'error')
        return redirect(request.referrer)

    new_user.first_name = request.form.get('firstname')
    new_user.last_name = request.form.get('lastname')
    new_user.email = request.form.get('email')
    new_user.phone_number = request.form.get('phone')

    db.session.commit()

    flash('Perfil atualizado com sucesso!', 'info')
    return redirect(request.referrer)
    
@admin_bp.route("/brand/insert", methods=['POST', 'GET'])
@login_required
def brand_insert():

    if request.method == "POST":
        
        brand_name = request.form.get('name')
        
        
        brand = Brand(name=brand_name)
        
        db.session.add(brand)
        db.session.commit()
        flash("MARCA INSERIDA COM SUCESSO!", 'info')
        return redirect(url_for('admin.list_brands'))

    else:   
        flash(f'Ocorreu um erro inesperado', 'error')



@admin_bp.route("/models/<id>", methods = ["POST"]) 
@login_required
def update_model(id):
       models = Model.query.get(id)

       if(models is None):
              flash('Este modelo nao existe', 'error')
              return redirect(url_for('admin.list_models'))

       request_data = request.form.get("name")

       if(request_data is None):
              flash('Nome do modelo nao pode vir vazio: ${name}', 'error')
              return redirect(url_for('admin.list_models'))

       if(request_data == models.name):
              flash('Esta marca j?? existe', 'error')
              return redirect(url_for('admin.list_models'))

       models.name = request_data

       try:
              db.session.commit()
              flash("MODELO ATUALIZADO COM SUCESSO!", 'info')
              return redirect(url_for('admin.list_models'))
       except Exception as e:
              print(e)
              flash(f'Ocorreu um erro inesperado', 'error')

@admin_bp.route('/models/delete/<id>')
@login_required
def delete_model(id):
    model_to_delete = Model.query.get_or_404(id)

    try:
        db.session.delete(model_to_delete)
        db.session.commit()
        flash("MODELO APAGADO COM SUCESSO!", 'info')
        return redirect(url_for('admin.list_models'))
    except:
        flash(f'Ocorreu um erro inesperado', 'error')

@admin_bp.route('/users/update/<id>', methods=['GET', 'POST'])
@login_required
def update_user(id):    
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash('Utilizador com este email nao existe', category='error')

        return redirect(url_for('admin.list_users'))

    user.username = request.form.get('username')    
    user.email = request.form.get('email')
    user.phone_number = request.form.get('phone_number')
    user.status = request.form.get('status')
    
    if request.form.get("status") is None:
        user.status = "Inactive"
    if request.form.get("status") == "on":
        user.status = "Active"

    db.session.commit()

    flash('Utilizador editado com sucesso', category='info')

    return redirect(url_for('admin.list_users'))

@admin_bp.route("/models/insert", methods=['POST', 'GET'])
@login_required
def models_insert():

    if request.method == "POST":
        
        model_name = request.form.get('name')
        brand_id_2 = request.form.get('selectBrand')
        
        models = Model(name=model_name, brand_id=brand_id_2)
        
        db.session.add(models)
        db.session.commit()
        flash("MODELO INSERIDO COM SUCESSO!", 'info')
        return redirect(url_for('admin.list_models'))

    else:   
        flash(f'Ocorreu um erro inesperado', 'error')

