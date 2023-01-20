from dataclasses import dataclass

@dataclass
class RideListDto:
    id: int
    driver_name: str
    driver_initials: str
    starting_location: str
    end_location: str
    status: str
    starting_date: str
    starting_hour: str
    total_places: str
    total_available_places: str
    is_joinable: bool

@dataclass
class RideDto:
    id: int
    starting_location: str
    end_location: str
    vehicle: str
    starting_date: str
    starting_hour: str
    total_places: str
    passengers: list
    is_joinable: bool
    
@dataclass
class PassengerListDto:
    id: int
    initials: str
 