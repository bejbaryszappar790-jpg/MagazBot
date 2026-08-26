from enum import Enum


class UserType(Enum):
    EXISTING = "existing"
    NEW = "new"



class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ChangingVariantAttribute(str, Enum):
    VARIANT_NAME = "variant_name"
    VARIANT_PRICE = "variant_price"
    VARIANT_QUANTITY = "variant_quantity"

class OperationMode(str, Enum):
    WRITE = "write"
    READ = "read"

class ThingType(str, Enum):
    PRODUCT = "product"
    VARIANT = "variant"

class GuiltytType(str, Enum):
    SERVER = "server"
    CLIENT = "client"


class RegressButtonType(str, Enum):
    CANCEL = "cancel"
    GO_BACK = "go_back"
    
