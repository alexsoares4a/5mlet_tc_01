from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

# Importações do FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importações locais
from database.database import get_db
from database.crud import get_user
from .schemas import TokenData
from database.models import User

# Configurações
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# Contexto para hashing de senhas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")

# Esquema OAuth2 para autenticação via Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto puro corresponde a uma senha hashed.

    Args:
        plain_password (str): A senha em texto puro fornecida pelo usuário.
        hashed_password (str): A senha hashed armazenada no banco de dados.

    Returns:
        bool: True se as senhas corresponderem, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Gera o hash de uma senha em texto puro.

    Args:
        password (str): A senha em texto puro a ser hashed.

    Returns:
        str: A senha hashed.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Cria um token de acesso JWT.

    Args:
        data (Dict[str, Any]): Os dados a serem incluídos no payload do token (ex., {"sub": username}).
        expires_delta (Optional[timedelta]): Opcional. O tempo de expiração do token.
                                             Se não fornecido, usa ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: O token JWT codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    
    to_encode.update({"exp": expire}) # Adiciona o tempo de expiração ao payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependência do FastAPI para obter o usuário autenticado a partir de um token JWT.
    Verifica a validade do token e a existência/atividade do usuário no banco de dados.

    Args:
        token (str): O token JWT extraído do cabeçalho Authorization (injetado por oauth2_scheme).
        db (Session): A sessão do banco de dados (injetada por get_db).

    Raises:
        HTTPException: Se as credenciais forem inválidas (token inválido, usuário não encontrado/inativo).

    Returns:
        User: O objeto User do SQLAlchemy correspondente ao usuário autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token JWT usando a chave secreta e o algoritmo.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extrai o 'sub' (subject), que geralmente é o username.
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception # Se o username não estiver no payload, credenciais inválidas.
        
        # Cria um objeto TokenData para validação e tipagem.
        token_data = TokenData(username=username)
    except JWTError:
        # Captura erros de JWT (ex., token expirado, assinatura inválida).
        raise credentials_exception
    
    # Busca o usuário no banco de dados usando o username do token.
    user = get_user(db, username=token_data.username)

    # Verifica se o usuário existe e se está ativo.
    if user is None or not user.is_active:
        raise credentials_exception # Se não encontrado ou inativo, credenciais inválidas.
    return user # Retorna o objeto User autenticado.
