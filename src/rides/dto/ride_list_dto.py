from dataclasses import dataclass

@dataclass
class RideListDto:
    driver_name: str
    starting_location: str
    status: str
    starting_date: str
    starting_hour: str
    total_places: str
    total_available_places: str