from pydantic import BaseModel


class UserContext(BaseModel):
    user_id: str
    role: str


class Citation(BaseModel):
    source: str
