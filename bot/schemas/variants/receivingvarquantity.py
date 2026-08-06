from pydantic import BaseModel, Field


class ReceivingVarQuantity(BaseModel):
    quantity : int
    parent_id : int
    var_name : str = Field(min_length = 1)
    var_price : float
    admin_id : int