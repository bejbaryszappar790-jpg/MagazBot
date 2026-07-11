class BotError(Exception):
    "Самая универсальная ошибка. От него идет все."
    pass



class DataBaseError(BotError):
    "Любая ошибка связанное с базами данных"
    pass

class PydanticError(BotError):
    "Любая ошибка с валидацией от pydantic"
    pass

class RoleError(BotError):
    "Любая ошибка которая связанно с ролем пользователя."
    pass

class DuplicateError(BotError):
    "Ошибка которая сработает если существет уже такое товар/вариянт и т.д"
    pass