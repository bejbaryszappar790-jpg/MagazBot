from pydantic import BaseModel

class SessionStart_In(BaseModel):
    user_id : int


class SessionStart_Out(BaseModel):
    response : str