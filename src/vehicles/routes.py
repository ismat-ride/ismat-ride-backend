from flask import render_template, request
from src.extensions import ITEMS_PER_PAGE
from src.rides.rides import Ride
from src.users.users import Brand, Model, Vehicle
from src.vehicles import vehicles_bp
from src.vehicles.dto.vehicles_dto import VehicleDto

@vehicles_bp.route("/list")
def vehicles_list():
    page = request.args.get('page', 1, type=int)

    query = Vehicle.query

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
            VehicleDto(vehicle.model.brand.name, vehicle.model.name, vehicle.color, vehicle.license_plate) 
        )

    response['items'] = vehicle_list

    if vehicle_list.__len__() == 0:
        return(render_template("vehicle/no_data.html"))

    return render_template("vehicle/index.html", vehicles = response)    

