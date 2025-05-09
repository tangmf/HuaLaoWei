from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str

class UserSignIn(BaseModel):
    username: str
    password_hash: str
