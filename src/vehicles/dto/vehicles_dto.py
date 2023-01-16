from dataclasses import dataclass

@dataclass
class VehicleDto:
    id:str
    brand: str
    model: str
    color: str
    license_plate: str
    seats: str