from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurações
from config import DATABASE_URL

# Cria o motor (engine) do SQLAlchemy, que gerencia a conexão com o banco de dados.
engine = create_engine(DATABASE_URL)

# Cria uma fábrica de sessões local.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria uma base declarativa para os modelos do SQLAlchemy.
Base = declarative_base()

# Função para injetar a sessão do banco de dados
def get_db():
    """
    Retorna uma sessão de banco de dados para uso em dependências do FastAPI.
    Garante que a sessão seja fechada corretamente após o uso.
    """
    db = SessionLocal()
    try:
        yield db  # Fornece a sessão para a rota que a solicitou
    finally:
        db.close() # Garante que a sessão seja fechada, liberando recursos

Session = SessionLocal 

def create_tables():
    """
    Cria todas as tabelas no banco de dados que são definidas pelos modelos
    que herdam da Base declarativa.
    Útil para inicializar o banco de dados em desenvolvimento.
    """
    Base.metadata.create_all(bind=engine)
