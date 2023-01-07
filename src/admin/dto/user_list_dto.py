from dataclasses import dataclass

@dataclass
class UserListDto:
    email: str
    full_name: str
    phone_number: str
    student_number: str
    status: str
    initials: str
