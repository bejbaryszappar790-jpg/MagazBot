from typing import Annotated

from pydantic import BaseModel, StringConstraints

from bot.enums import ChangingVariantAttribute
from bot.models import Variants


class ChangeVariantBaseSchema(BaseModel):
    variant_obj : Variants
    variant_attribute : ChangingVariantAttribute
    admin_id : int

class ChangeVariantNameSchema(ChangeVariantBaseSchema):
    new_attibute : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]


class ChangeVariantPriceSchema(ChangeVariantNameSchema):
    pass
    
class ChangeVariantQuantitySchema(ChangeVariantBaseSchema):
    new_attibute : int