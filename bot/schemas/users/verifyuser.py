from pydantic import BaseModel


class VerifyUser(BaseModel):
    user_id : int