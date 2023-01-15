from dataclasses import dataclass

@dataclass
class VehicleDto:
    brand: str
    model: str
    color: str
    license_plate: str