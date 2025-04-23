from pydantic import BaseModel
import uuid

class UserDto(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    role: str
    
    class Config:
        from_attributes = True