from .database import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    """
    Modelo SQLAlchemy para representar a tabela 'users' no banco de dados.
    Armazena informações de usuários, incluindo credenciais para autenticação.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) # Armazena o hash da senha, nunca a senha em texto puro.
    is_active = Column(Boolean, default=False) # Indica se a conta do usuário está ativa (ex., após verificação de e-mail).
    verification_token = Column(String(255), nullable=True) # Token para ativação de conta ou redefinição de senha.
