from typing import Annotated

from pydantic import BaseModel, StringConstraints


class GetParentIdForGetVariant(BaseModel):
    parent_name : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]
    parent_id : int
    user_id : int