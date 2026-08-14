from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class ReceivingVarQuantity(BaseModel):
    quantity : int
    parent_id : int
    var_name : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]
    var_price : Decimal
    admin_id : int