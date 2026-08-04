from pydantic import BaseModel, Field
from bot.enums import OperationMode

class GetProductNameForVariant(BaseModel):
    admin_id : int
    parent_name : str = Field(min_length = 1)
    mode : OperationMode