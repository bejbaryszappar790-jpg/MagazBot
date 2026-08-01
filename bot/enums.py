from enum import Enum


class UserType(Enum):
    EXISTING = "existing"
    NEW = "new"



class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"