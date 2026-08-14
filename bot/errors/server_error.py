from bot.errors.base_error import BotError


class ServerError(BotError):
    """
    Base class for all internal server and developer errors.
    """   
    def __init__(self, log_message : str):
        self.log_message = log_message
        super().__init__(log_message)


class DataBaseError(ServerError):
    """
    Any error which is related to the DB
    """
    

class ServerPydanticError(ServerError):
    """
    Error which is related to pydantic validation error but not caused by user/admin.
    """
    


class ServerAbsenceError(ServerError):
    """
    Error which is caused when some data is None by server's fault 
    """
    

class ServerValidationError(ServerError):
    """
    Error which is caused by servers unvalidable variants which is not related clients.
    """
    

class RecheckError(ServerError):
    """
    Caused when we get error during the rechecking already checked data, variables. 
    """
    

class ServerMissingDataError(ServerError):
    """
    MissinDataError but caused the side of server
    """