from pydantic import BaseModel, Field

class CreatingProduct(BaseModel):
    admin_id : int
    parent_name : str = Field(min_length = 1)