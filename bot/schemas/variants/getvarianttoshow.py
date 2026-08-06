from pydantic import BaseModel, Field


class GetVariantToShow(BaseModel):
    parent_name : str = Field(min_length = 1)
    parent_id : int
    variant_id : int
    user_id : int