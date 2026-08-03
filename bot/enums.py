from enum import Enum


class UserType(Enum):
    EXISTING = "existing"
    NEW = "new"



class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ChangingData(str, Enum):
    VARIANT_NAME = "variant_name"
    VARIANT_PRICE = "variant_price"
    VARIANT_QUANTITY = "variant_quantity"

class OperationMode(str, Enum):
    WRITE = "write"
    READ = "read"