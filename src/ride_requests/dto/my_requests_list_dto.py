from dataclasses import dataclass

@dataclass
class MyRequestsListDto:
    id: str
    source: str
    destination: str
    status: str
    starting_date: str
    starting_hour: str
    isCancelable: bool