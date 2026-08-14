from bot.errors.base_error import BotError


class ClientError(BotError):
    """
    Universial error which is caused by client side.
    """

    def __init__(self, user_message : str, log_message : str, clear_state : bool = False):
        self.user_message = user_message
        self.log_message = log_message
        self.clear_state = clear_state
        super().__init__(log_message)


class RoleError(ClientError):
    """
    Any error which is related to user role.
    """
    


class DuplicateError(ClientError):
    """
    The error which is caused when admin wants to create products/variants which is already exists.
    """
    


class AbsenceError(ClientError):
    """
    The error which is caused when user/admin searches not existing product/variant.
    """



class BusinessLogicError(ClientError):
    """
    The error which is related to every buissnes logic error.
    """
    


class MissingDataError(ClientError):
    """
    The error which is caused when nullable data is None.
    """
    

class ClientPydanticError(ClientError):
    """
    Any error which is related to pydantic validation error which is caused by user/admin.
    """
    

class SimpleValidationError(ClientError):
    """
    Any validation error which is not related to pydantic.
    """
    

class UnknownUserError(ClientError):
    """
    Error which is caused when unauthorized user wants to do smth.
    """
    


