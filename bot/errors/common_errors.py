class BotError(Exception):
    """
    Most universal error and only this error is used in handlers.
    """   
    pass



class DataBaseError(BotError):
    """
    Any error which is related to the DB
    """
    pass

class PydanticError(BotError):
    """
    Any error which is related to pydantic validation.
    """
    pass

class SimpleValidationError(BotError):
    """
    Any validation error which is not related to pydantic.
    """
    pass


class RoleError(BotError):
    """
    Any error which is related to user role.
    """
    pass

class DuplicateError(BotError):
    """
    The error which is caused when admin wants to create products/variants which is already exists.
    """
    pass

class AbsenseError(BotError):
    """
    The error which is caused when user/admin searchs not existing product/variant.
    """

class BuisnessLogicError(BotError):
    """
    The error which is related to every buissnes logic error.
    """