from pydantic import BaseModel


class ReturnVariantTableSchema(BaseModel):
    parent_id : int
    user_id : int