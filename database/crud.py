from sqlalchemy.orm import Session
from .models import User
from typing import Optional 

def get_user(db: Session, username: str) -> Optional[User]:
    """
    Busca um usuário no banco de dados pelo nome de usuário.

    Args:
        db (Session): A sessão do banco de dados.
        username (str): O nome de usuário a ser buscado.

    Returns:
        Optional[User]: O objeto User se encontrado, caso contrário, None.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Busca um usuário no banco de dados pelo endereço de e-mail.

    Args:
        db (Session): A sessão do banco de dados.
        email (str): O endereço de e-mail a ser buscado.

    Returns:
        Optional[User]: O objeto User se encontrado, caso contrário, None.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, hashed_password: str, token: str) -> User:
    """
    Cria um novo usuário no banco de dados.

    Args:
        db (Session): A sessão do banco de dados.
        username (str): O nome de usuário do novo usuário.
        email (str): O endereço de e-mail do novo usuário.
        hashed_password (str): A senha do usuário já em formato hash.
        token (str): O token de verificação (mantido para compatibilidade com a estrutura existente).

    Returns:
        User: O objeto User recém-criado.
    """
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        verification_token=token,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_id(db: Session, user_id: int) -> bool:
    """
    Deleta um usuário do banco de dados pelo seu ID.

    Args:
        db (Session): A sessão do banco de dados.
        user_id (int): O ID do usuário a ser deletado.

    Returns:
        bool: True se o usuário foi deletado com sucesso, False caso contrário.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
