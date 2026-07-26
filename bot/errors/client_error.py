from bot.errors.base_error import BotError



class ClientError(BotError):
    """
    Universial error which is caused by client side.
    """

    def __init__(self, user_message : str, log_message : str):
        self.user_message = user_message
        self.log_message = log_message


class RoleError(ClientError):
    """
    Any error which is related to user role.
    """
    pass


class DuplicateError(ClientError):
    """
    The error which is caused when admin wants to create products/variants which is already exists.
    """
    pass


class AbsenseError(ClientError):
    """
    The error which is caused when user/admin searches not existing product/variant.
    """



class BuisnessLogicError(ClientError):
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
    pass

class SimpleValidationError(ClientError):
    """
    Any validation error which is not related to pydantic.
    """
    pass


