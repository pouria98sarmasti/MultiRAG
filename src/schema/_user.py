import uuid
from pydantic import BaseModel



class UserCreateOutput(BaseModel):
    username: str
    id: uuid.UUID



class ListAllUsersOutput(BaseModel):
    username: str
    id: uuid.UUID