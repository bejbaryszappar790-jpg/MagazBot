from typing import TypeVar

from pydantic import BaseModel, ValidationError

from bot.errors.client_error import ClientPydanticError
from bot.errors.server_error import ServerMissingDataError

T = TypeVar("T", bound = BaseModel)

def validate_user_input(schema : type[T], data : dict | str, user_id : int | None, validated_data : str):
    try:
        if user_id is None:
            raise ServerMissingDataError("Не было передано user_id в helper")
        
        if isinstance(data, str):
            return schema.model_validate_json(data)
        return schema.model_validate(data)

    except ValidationError as e:
        invalid_fields = "; ".join(f"{'->'.join(str(loc) for loc in error['loc'])} : {error['msg']}" for error in e.errors())

        raise ClientPydanticError(f"Вы ввели неправильную {validated_data}!", f"Pydantic не смог валидировать данные  {invalid_fields}  пользователя {user_id}.")
    