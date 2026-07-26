from bot.errors.base_error import BotError

class ServerError(BotError):
    """
    Base class for all internal server and developer errors.
    """   
    pass



class DataBaseError(ServerError):
    """
    Any error which is related to the DB
    """
    pass

class ServerPydanticError(ServerError):
    """
    Error which is related to pydantic validation error but not caused by user/admin.
    """
    pass
    

