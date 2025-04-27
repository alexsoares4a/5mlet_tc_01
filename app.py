from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import secrets
from sqlalchemy.orm import Session

# Importações para o site
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importações dos módulos de autenticação
from auth.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, verify_password, get_current_user
from auth.schemas import UserCreate, Token
from auth.email_service import send_verification_email

# Importações dos módeulos de banco de dados
from database.database import get_db, create_tables
from database.crud import get_user, create_user, verify_user, delete_user

# Importação do módulo de captura dos dados do site da embrapa
from scraper import scrape_embrapa

# Cria as tabelas ao iniciar o app
create_tables()

# --- Configurações da API ---
app = FastAPI(    
    title="VitiBrasil API",
    description="API para acessar dados de vitivinicultura da Embrapa",
    version="1.0.0",
    contact={
        "name": "Alex",
        "email": "alexssonline@gmail.com",
    },
    license_info={
        "name": "MIT License",
    },
)
# Monta a pasta frontend como arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Rotas da API ---
# Rota raiz
@app.get("/", 
         summary="Página Inicial", 
         description="Retorna a página inicial do site.")
async def read_index():
    return FileResponse("static/index.html")

# Rota de registro (cadastro de usuário)
@app.post(
    "/register",
    response_model=Token,
    summary="Registrar Usuário",
    description="Cria um novo usuário no sistema e envia um e-mail de verificação.",
    responses={
        200: {"description": "Usuário registrado com sucesso. Retorna um token JWT."},
        500: {"description": "Erro ao registrar o usuário."}
    }
)
async def register(user: UserCreate, db: Session = Depends(get_db)):    
    try:
        hashed_password = get_password_hash(user.password)
        verification_token = secrets.token_urlsafe(32)
        
        create_user(
            db=db,
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            token=verification_token
        )
        
        # Tenta enviar e-mail mas não falha se não conseguir
        email_enviado = send_verification_email(user.email, verification_token)
        
        if not email_enviado:
            print("Aviso: E-mail não enviado, mas usuário foi criado")
        
        return {"access_token": create_access_token({"sub": user.username}), "token_type": "bearer"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no registro: {str(e)}")

# Rota de verificação de e-mail
@app.get(
    "/verify-email",
    summary="Verificar E-mail",
    description="Verifica o token enviado por e-mail para ativar a conta do usuário.",
    responses={
        200: {"description": "E-mail verificado com sucesso."},
        400: {"description": "Token inválido ou expirado."}
    }
)
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = verify_user(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    return {"message": "E-mail verificado com sucesso!"}

# Rota de login (gera token JWT)
@app.post(
    "/login",
    response_model=Token,
    summary="Login do Usuário",
    description="Autentica o usuário e retorna um token JWT.",
    responses={
        200: {"description": "Login bem-sucedido. Retorna um token JWT."},
        401: {"description": "Credenciais inválidas."},
        400: {"description": "E-mail não verificado."}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = get_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="E-mail não verificado")
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rota de Logout
@app.post(
    "/logout", 
    summary="Logoff do Usuário", 
    description="Remove a sessão do usuário.",
    responses={
        200: {"description": "Sessão encerrada com sucesso."},
        401: {"description": "Não autorizado. Token inválido ou ausente."}
    }
)
async def logout():
    return {"message": "Sessão encerrada com sucesso."}

# Rota de Excluir Conta do Usuário
@app.delete(
    "/delete-user",
    summary="Excluir Conta do Usuário",
    description="Permite que o usuário exclua sua conta permanentemente.",
    responses={
        200: {"description": "Conta excluída com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Usuário não encontrado."}
    }
)
async def delete_user(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verifica se o usuário existe
    user = get_user(db, username=current_user)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    # Exclui o usuário
    delete_user(db, user.id)
    return {"message": "Sua conta foi excluída permanentemente."}

# --- ROTAS DO WEB SCRAPER --- #

# Consultar Produção
@app.get(
    "/producao/{ano}",
    summary="Consultar Produção",
    description="Retorna dados de produção vitivinícola para o ano especificado.",
    responses={
        200: {"description": "Dados de produção retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Rota não encontrada."}
    }
)
def get_producao(
    ano: int, 
    current_user: str = Depends(get_current_user)
):
    return scrape_embrapa(ano, "opt_02")

# Consultar Processamento
@app.get(
    "/processamento/{tipo}/{ano}",
    summary="Consultar Processamento",
    description="Retorna dados de processamento vitivinícola para o tipo e ano especificados.",
    responses={
        200: {"description": "Dados de processamento retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Rota não encontrada."}
    }
)
def get_processamento(
    tipo: str, 
    ano: int, 
    current_user: str = Depends(get_current_user)
):
    return scrape_embrapa(ano, "opt_03", tipo)

# Consultar Comercialização
@app.get(
    "/comercializacao/{ano}",
    summary="Consultar Comercialização",
    description="Retorna dados de comercialização vitivinícola para o ano especificado.",
    responses={
        200: {"description": "Dados de comercialização retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Rota não encontrada."}
    }
)
def get_comercializacao(
    ano: int, 
    current_user: str = Depends(get_current_user)
):
    return scrape_embrapa(ano, "opt_04")

# Consultar Importação
@app.get(
    "/importacao/{produto}/{ano}",
    summary="Consultar Importação",
    description="Retorna dados de importação vitivinícola para o produto e ano especificados.",
    responses={
        200: {"description": "Dados de importação retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Rota não encontrada."}
    }
)
def get_importacao(
    produto: str, 
    ano: int, 
    current_user: str = Depends(get_current_user)
):
    return scrape_embrapa(ano, "opt_05", produto)

# Consultar Exportação
@app.get(
    "/exportacao/{produto}/{ano}",
    summary="Consultar Exportação",
    description="Retorna dados de exportação vitivinícola para o produto e ano especificados.",
    responses={
        200: {"description": "Dados de exportação retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Rota não encontrada."}
    }
)
def get_exportacao(
    produto: str, 
    ano: int, 
    current_user: str = Depends(get_current_user)
):
    return scrape_embrapa(ano, "opt_06", produto)
