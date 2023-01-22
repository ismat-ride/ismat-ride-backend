from dataclasses import dataclass

@dataclass
class RequestsToMyRidesListDto:
    id: str
    passanger_name: str
    initials: str
    starting_location: str
    end_location:str
    status: str
    starting_date: str
    starting_hour: str
    is_available: str
   