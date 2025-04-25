from pydantic import BaseModel

class TokenData(BaseModel):
    username: str | None = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
