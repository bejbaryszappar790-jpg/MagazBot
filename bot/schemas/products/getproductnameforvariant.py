from typing import Annotated

from pydantic import BaseModel, StringConstraints

from bot.enums import OperationMode


class GetProductNameForVariant(BaseModel):
    user_id : int
    parent_name : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]
    mode : OperationMode