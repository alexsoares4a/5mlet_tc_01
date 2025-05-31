from pydantic import BaseModel, EmailStr

class TokenData(BaseModel):
    """
    Schema para o payload do token JWT.
    Contém o nome de usuário (subject) do token.
    """
    username: str | None = None

class UserCreate(BaseModel):
    """
    Schema para a criação de um novo usuário.
    Usado para validar os dados de entrada no endpoint de registro.
    """
    username: str
    email: EmailStr
    password: str 

class UserLogin(BaseModel):
    """
    Schema para as credenciais de login do usuário.
    """
    username: str
    password: str

class Token(BaseModel):
    """
    Schema para o retorno de um token de acesso.
    """
    access_token: str
    token_type: str
