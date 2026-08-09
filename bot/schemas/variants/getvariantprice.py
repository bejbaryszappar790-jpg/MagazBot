from pydantic import BaseModel


class GetVariantPrice(BaseModel):
    input_price : str
    admin_id : int
    