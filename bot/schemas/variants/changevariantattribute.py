from typing import Annotated

from pydantic import BaseModel, StringConstraints

from bot.enums import ChangingVariantAttribute


class ChangeVariantBaseSchema(BaseModel):
    variant_id : int
    variant_attribute : ChangingVariantAttribute
    admin_id : int

class ChangeVariantNameSchema(ChangeVariantBaseSchema):
    new_attribute : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]


class ChangeVariantPriceSchema(ChangeVariantNameSchema):
    pass
    
class ChangeVariantQuantitySchema(ChangeVariantBaseSchema):
    new_attribute : int