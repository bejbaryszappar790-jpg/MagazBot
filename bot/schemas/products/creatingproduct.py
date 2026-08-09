from typing import Annotated

from pydantic import BaseModel, StringConstraints


class CreatingProduct(BaseModel):
    admin_id : int
    parent_name : Annotated[str, StringConstraints(strip_whitespace = True, min_length = 1)]