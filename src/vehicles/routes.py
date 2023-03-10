
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from src.extensions import db,ITEMS_PER_PAGE
from src.rides.rides import Ride
from src.users.users import Brand, Model, Vehicle
from src.vehicles import vehicles_bp
from src.vehicles.dto.vehicles_dto import VehicleDto

@vehicles_bp.route("/list")
@login_required
def vehicles_list():
    page = request.args.get('page', 1, type=int)

    query = Vehicle.query

    models_list = Model.query.all()

    if request.args.get("model"):
        query = query.join(Model, Vehicle.model).filter(Model.name.contains(request.args.get("model")))
    if request.args.get("brand"):
        query = query.join(Model, Vehicle.model).join(Brand, Model.brand).filter(Brand.name.contains(request.args.get("brand")))
    if request.args.get("vin"):
        query = query.filter(Vehicle.license_plate.contains(request.args.get("vin")))

    query = query.paginate(page=page, per_page=ITEMS_PER_PAGE)

    response = {'items': list(), 'iter_pages': query.iter_pages, 'page': page, 'pages': query.pages, 'next_num': query.next_num}

    vehicle_list = list()
    
    for vehicle in query:
        vehicle_list.append(
            VehicleDto(vehicle.id, vehicle.model.brand.name, vehicle.model.name, vehicle.color, vehicle.license_plate, vehicle.seats) 
        )

    response['items'] = vehicle_list

    if vehicle_list.__len__() == 0:
        return(render_template("vehicle/no_data.html"))

    return render_template("vehicle/index.html", vehicles = response, models = models_list)    

@vehicles_bp.route("/delete/<id>", methods = ["POST"])
@login_required
def delete_vehicle(id):
    
    vehicle_to_delete = db.session.query(Vehicle).filter(Vehicle.id == id).one()

    if vehicle_to_delete is None:
        flash('Este veículo não existe', "error")
        return redirect(url_for('vehicles.vehicles_list'))

    exists = bool(db.session.query(Ride).filter_by(vehicle_id = id).first())
   
    if exists is True:
        flash("Veículo está a ser utilizado, não pode ser apagado!" , "error")
        return redirect(url_for('vehicles.vehicles_list'))
   
    db.session.delete(vehicle_to_delete)
    db.session.commit()

    flash("Veículo deletado com sucesso!" , "info")
    return redirect(url_for('vehicles.vehicles_list'))

@vehicles_bp.route("/edit/<id>", methods = ["POST"])
@login_required
def edit_vehicle(id):
    vehicle = Vehicle.query.filter_by(id=id).first()

    if vehicle is None:
        flash('Não existe este veículo', 'error')
        return redirect(url_for('vehicles.vehicles_list'))
    if request.form.get('model') is None or request.form.get('model') == "":
        flash('Insira um modelo!', 'error')
        return redirect(url_for('vehicles.vehicles_list'))
    if request.form.get('color') is None or request.form.get('color') == "":
        flash('Cor invalida!', 'error')
        return redirect(url_for('vehicles.vehicles_list'))
    if request.form.get('vin') is None or request.form.get('vin') == "":
        flash('Matricula invalida!', 'error')
        return redirect(url_for('vehicles.vehicles_list'))
    if request.form.get('places') is None or request.form.get('places') == "":
        flash('Número de lugares invalido!', 'error')
        return redirect(url_for('vehicles.vehicles_list'))            

    vehicle.model_id = request.form.get('model')
    vehicle.color = request.form.get('color')
    vehicle.license_plate = request.form.get('vin')
    vehicle.seats = request.form.get('places')

    db.session.commit()

    flash('Veículo atualizado com sucesso', 'info')
    return redirect(url_for('vehicles.vehicles_list'))  

@vehicles_bp.route("/create", methods = ["POST"])
@login_required
def create_vehicle():

    vin = request.form.get('vin')

    if vin is None or vin == "":
        flash("Vin invalido!", "error")
        return redirect(request.referrer)

    color = request.form.get('color')

    if color is None or color == "":
        flash("Cor invalida!", "error")
        return redirect(request.referrer)

    seats = request.form.get('places')

    if seats is None or seats == "":
        flash("Lugares invalidos!", "error")
        return redirect(request.referrer)

    model_id = request.form.get('model')

    if model_id is None or model_id == "":
        flash("Modelo invalido!", "error")
        return redirect(request.referrer)

    new_vehicle = Vehicle(user_id = current_user.id,
    license_plate = vin,
    color = color,
    seats = seats,
    model_id = model_id)
    
    db.session.add(new_vehicle)
    db.session.commit()

    flash("Veículo adicionado com sucesso!", 'info')
    return redirect(request.referrer)