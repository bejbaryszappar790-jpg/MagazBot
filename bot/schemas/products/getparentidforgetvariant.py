from pydantic import BaseModel, Field

class GetParentIdForGetVariant(BaseModel):
    parent_name : str = Field(min_length = 1)
    parent_id : int
    user_id : int