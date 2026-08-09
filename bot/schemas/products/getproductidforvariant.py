from pydantic import BaseModel


class GetProductIdForVariant(BaseModel):
    parent_id : int
    admin_id : int