from pydantic import BaseModel, Field

class GetVariantName(BaseModel):
    variant_name : str = Field(min_length = 1)
    parent_id : int
    admin_id : int
    