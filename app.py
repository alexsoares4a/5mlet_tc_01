from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel
import secrets
from sqlalchemy.orm import Session 

# Importações para o site
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importações dos módulos internos
from auth.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, verify_password
from database.database import get_db, SessionLocal
from database.models import User
from database.database import create_tables
from database.crud import get_user, create_user, verify_user
from auth.schemas import UserCreate, Token, TokenData
from auth.email_service import send_verification_email
from scraper import scrape_embrapa



# Cria as tabelas ao iniciar o app
create_tables()

# --- Configurações da API ---
app = FastAPI()
# Monta a pasta frontend como arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Rotas da API ---

# Rota raiz
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Rota de registro (cadastro de usuário)
@app.post("/register", response_model=Token)
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
@app.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = verify_user(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    return {"message": "E-mail verificado com sucesso!"}

# Rota de login (gera token JWT)
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

# --- Rotas do Web Scraper ---

@app.get("/producao/{ano}")
def get_producao(ano: int):
    return scrape_embrapa(ano, "opt_02")

@app.get("/processamento/{tipo}/{ano}")
def get_processamento(tipo: str, ano: int):
    subopcoes = tipo
    return scrape_embrapa(ano, "opt_03", subopcoes)

@app.get("/comercializacao/{ano}")
def get_comercializacao(ano: int):
    return scrape_embrapa(ano, "opt_04")

@app.get("/importacao/{produto}/{ano}")
def get_importacao(produto: str, ano: int):
    subopcoes = produto
    return scrape_embrapa(ano, "opt_05", subopcoes)

@app.get("/exportacao/{produto}/{ano}")
def get_exportacao(produto: str, ano: int):
    subopcoes = produto
    return scrape_embrapa(ano, "opt_06", subopcoes)
