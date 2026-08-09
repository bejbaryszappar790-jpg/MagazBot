from typing import Annotated

from pydantic import BaseModel, StringConstraints


class GetVariantName(BaseModel):
    variant_name : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]
    parent_id : int
    admin_id : int
    