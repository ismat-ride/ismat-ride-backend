from dataclasses import dataclass

@dataclass
class UserListDto:
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: str
    student_number: str
    status: str
    initials: str