from dataclasses import dataclass

@dataclass
class RideRequestDto:
    passanger_name: str
    driver_name: str
    starting_location: str
    status: str
    starting_date: str
    starting_hour: str
   