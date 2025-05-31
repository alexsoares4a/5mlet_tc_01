from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

# Importações para o site
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importações dos módulos de autenticação
from auth.security import create_access_token, get_password_hash, verify_password, get_current_user
from auth.schemas import UserCreate, Token

# Importações dos módeulos de banco de dados
from database.database import get_db
from database.crud import(
    get_user, 
    get_user_by_email,
    create_user,
    delete_user_id
)

# Importa o modelo User do SQLAlchemy
from database.models import User

# Importação do módulo de captura dos dados do site da embrapa
from services.scraper import scrape_embrapa

# Importação da função auxiliar para lidar com o fallback para CSV
from services.fallback import get_data_from_csv_fallback

# Importação dos enumeradores
from schemas.enums import ProcessamentoTipo, ImportacaoTipo, ExportacaoTipo

from config import ACCESS_TOKEN_EXPIRE_MINUTES

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
# Monta a pasta 'static' como arquivos estáticos do template Bootstrap
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Rotas da API ---
# Rota raiz
@app.get(
    "/", 
    summary="Página Inicial", 
    tags=["Redirecionamento"],
    description="Retorna a página inicial do site."
)
async def read_index():
    """
    Retorna o arquivo HTML principal da aplicação.
    """
    return FileResponse("static/index.html")

# Rota de registro (cadastro de usuário)
@app.post(
    "/register",
    tags=["Cadastro e Autenticação"],
    summary="Registrar Usuário",
    description="Cria um novo usuário no sistema.",
    responses={
        200: {"description": "Usuário cadatrado com sucesso."},
        400: {"description": "Nome de usuário ou e-mail já cadastrado."},
        500: {"description": "Erro interno ao cadastrar o usuário."}
    }
)
async def register(
    user: UserCreate, # Recebe os dados do usuário conforme o schema UserCreate
    db: Session = Depends(get_db) # Injeta a sessão do banco de dados
):   
    """
    Endpoint para registrar um novo usuário.
    Verifica se o nome de usuário ou e-mail já existem antes de criar o usuário.
    """
    try: 
        # Verifica se o usuário ou e-mail já existem
        existing_user = get_user(db, username=user.username)
        existing_email = get_user_by_email(db, email=user.email)
        if existing_user or existing_email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário ou e-mail já cadastrado"
            )
        
        # Gera senha hash antes de armazenar
        hashed_password = get_password_hash(user.password)

        # Cria o novo usuário no banco de dados
        create_user(
            db=db,
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            token=None
        )

        return {"message": "Usuário registrado com sucesso."}
    
    except HTTPException as http_exc:
        # Captura HTTPException para re-lançar sem rollback desnecessário
        raise http_exc
    except Exception as e:
        db.rollback() # Garante que a transação seja revertida em caso de erro
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no cadastro: {str(e)}")

# Rota de login (gera token JWT)
@app.post(
    "/login",    
    tags=["Cadastro e Autenticação"],
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
    form_data: OAuth2PasswordRequestForm = Depends(),  # Injeta dados do formulário de login
    db: Session = Depends(get_db) # Injeta a sessão do banco de dados
) -> Token:
    """
    Endpoint para autenticação de usuário.
    Verifica as credenciais e, se válidas, gera e retorna um token de acesso JWT.
    """
    user = get_user(db, username=form_data.username)

    # Verifica se o usuário existe e se a senha está correta
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Verifica se o usuário está ativo (mesmo que a verificação por e-mail esteja desativada)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo. Entre em contato com o suporte.")
    
    # Cria o token de acesso JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rota de Logout
@app.post(
    "/logout", 
    tags=["Cadastro e Autenticação"],
    summary="Logoff do Usuário", 
    description="Remove a sessão do usuário.",
    responses={
        200: {"description": "Sessão encerrada com sucesso."},
        401: {"description": "Não autorizado. Token inválido ou ausente."}
    }
)
async def logout():
    """
    Endpoint de logout.
    Como JWTs são stateless, este endpoint apenas retorna uma mensagem de sucesso.
    """
    return {"message": "Sessão encerrada com sucesso."}

# Rota de Excluir Conta do Usuário
@app.delete(
    "/delete-user",
    tags=["Cadastro e Autenticação"],
    summary="Excluir Conta do Usuário",
    description="Permite que o usuário exclua sua conta permanentemente.",
    responses={
        200: {"description": "Conta excluída com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Usuário não encontrado."}
    }
)
async def delete_user(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
) -> dict:
    """
    Endpoint para exclusão da conta do usuário autenticado.
    """

    try:
        success = delete_user_id(db, current_user.id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado para exclusão.")
        return {"message": "Sua conta foi excluída permanentemente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao excluir usuário: {str(e)}")

# --- ROTAS DO WEB SCRAPER --- #

# Consultar Produção
@app.get(
    "/producao/{ano}",
    tags=["Rotas de Web Scrapper"],
    summary="Consultar Produção",
    description="Retorna dados de produção vitivinícola para o ano especificado.",
    responses={
        200: {"description": "Dados de produção retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Dados não encontrados para o ano especificado."},
        500: {"description": "Erro interno do servidor."}
    }
)
async def get_producao(
    ano: int = Path(
        ..., # Indica que é um parâmetro obrigatório
        ge = 1970, # Greater than or equal (maior ou igual a)
        le = 2023, # Less than or equal (menor ou igual a)
        description="Ano da consulta (entre 1970 e 2023)."
    ),
    current_user: str = Depends(get_current_user)
) -> list:
    """
    Endpoint para consultar dados de produção vitivinícola.
    Tenta raspar os dados do site da Embrapa; em caso de falha, usa um arquivo CSV local.
    """

    try:
        # Tenta obter os dados do site da Embrapa
        data = scrape_embrapa(ano, "opt_02")
        if data: # Verifica se scrape_embrapa retornou dados
            return data
        else:
            # Se scrape_embrapa não retornou dados, tenta o fallback
            raise ValueError("Web scraping não retornou dados, tentando fallback para CSV.")
    except Exception as e:
        # Lógica de fallback para CSV
        df_columns_map = {"produto": "produto", str(ano): "quantidade"}
        return get_data_from_csv_fallback("Producao.csv", ano, df_columns_map, sep=";")

# Consultar Processamento
@app.get(
    "/processamento/{tipo}/{ano}",
    tags=["Rotas de Web Scrapper"],
    summary="Consultar Processamento",
    description="Retorna dados de processamento vitivinícola para o tipo e ano especificados.",
    responses={
        200: {"description": "Dados de processamento retornados com sucesso."},
        400: {"description": "Tipo de processamento inválido."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Dados não encontrados para o tipo e ano especificados."},
        500: {"description": "Erro interno do servidor."}
    }
)
def get_processamento(
    tipo: ProcessamentoTipo = Path(
        ..., # Indica que é obrigatório
        description = "Tipo de processamento de uvas. Opções válidas:\n"
                    "- `subopt_01`: Uvas Viníferas\n"
                    "- `subopt_02`: Uvas Americanas e Híbridas\n"
                    "- `subopt_03`: Uvas de Mesa\n"
                    "- `subopt_04`: Uvas Sem Classificação"
    ),
    ano: int = Path(
        ..., # Indica que é um parâmetro obrigatório
        ge = 1970, # Greater than or equal (maior ou igual a)
        le = 2023, # Less than or equal (menor ou igual a)
        description="Ano da consulta (entre 1970 e 2023)."
    ),
    current_user: User = Depends(get_current_user)
) -> list:
    """
    Endpoint para consultar dados de processamento vitivinícola.
    Tenta raspar os dados do site da Embrapa; em caso de falha, usa um arquivo CSV local.
    """
    tipo_to_filename = {
        "subopt_01": "ProcessaViniferas.csv",
        "subopt_02": "ProcessaAmericanas.csv",
        "subopt_03": "ProcessaMesa.csv",
        "subopt_04": "ProcessaSemclass.csv"
    }

    try:
        data = scrape_embrapa(ano, "opt_03", tipo.value)
        if data:
            return data
        else:
            raise ValueError("Web scraping não retornou dados, tentando fallback para CSV.")
    except Exception as e:
        df_columns_map = {"cultivar": "cultivar", str(ano): "quantidade"}
        return get_data_from_csv_fallback(tipo_to_filename[tipo.value], ano, df_columns_map, sep=";")

# Consultar Comercialização
@app.get(
    "/comercializacao/{ano}",
    tags=["Rotas de Web Scrapper"],
    summary="Consultar Comercialização",
    description="Retorna dados de comercialização vitivinícola para o ano especificado.",
    responses={
        200: {"description": "Dados de comercialização retornados com sucesso."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Dados não encontrados para o ano especificado."},
        500: {"description": "Erro interno do servidor."}
    }
)

def get_comercializacao(
    ano: int, 
    current_user: User = Depends(get_current_user)
) -> list:
    """
    Endpoint para consultar dados de comercialização vitivinícola.
    Tenta raspar os dados do site da Embrapa; em caso de falha, usa um arquivo CSV local.
    """

    try:
        data = scrape_embrapa(ano, "opt_04")
        if data:
            return data
        else:
            raise ValueError("Web scraping não retornou dados, tentando fallback para CSV.")
    except Exception as e:
        df_columns_map = {"Produto": "produto", str(ano): "quantidade"}
        return get_data_from_csv_fallback("Comercio.csv", ano, df_columns_map, sep=";")

# Consultar Importação
@app.get(
    "/importacao/{produto}/{ano}",
    tags=["Rotas de Web Scrapper"],
    summary="Consultar Importação",
    description="Retorna dados de importação vitivinícola para o produto e ano especificados.",
    responses={
        200: {"description": "Dados de importação retornados com sucesso."},
        400: {"description": "Produto de importação inválido."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Dados não encontrados para o produto e ano especificados."},
        500: {"description": "Erro interno do servidor."}
    }
)
def get_importacao(
    produto: ImportacaoTipo = Path(
    ...,
    description="Tipo de importação vitivinícola. Opções válidas:\n"
                "- `subopt_01`: Vinhos de Mesa\n"
                "- `subopt_02`: Espumantes\n"
                "- `subopt_03`: Uvas Frescas\n"
                "- `subopt_04`: Uvas Passas\n"
                "- `subopt_05`: Suco de Uva"
    ),
    ano: int = Path(
        ...,
        ge=1970,
        le=2023,
        description="Ano da consulta (entre 1970 e 2023)."
    ),
    current_user: str = Depends(get_current_user)
) -> list:
    """
    Endpoint para consultar dados de importação vitivinícola.
    Tenta raspar os dados do site da Embrapa; em caso de falha, usa um arquivo CSV local.
    """
    tipo_to_filename = {
        "subopt_01": "ImpVinhos.csv",
        "subopt_02": "ImpEspumantes.csv",
        "subopt_03": "ImpFrescas.csv",
        "subopt_04": "ImpPassas.csv",
        "subopt_05": "ImpSuco.csv"
    }

    if produto not in tipo_to_filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Produto '{produto}' inválido.")

    try:
        data = scrape_embrapa(ano, "opt_05", produto)
        if data:
            return data
        else:
            raise ValueError("Web scraping não retornou dados, tentando fallback para CSV.")
    except Exception as e:
        df_columns_map = {"País": "pais", str(ano): "quantidade", f"{ano}.1": "valor_usd"}
        return get_data_from_csv_fallback(tipo_to_filename[produto], ano, df_columns_map, sep="\t")

# Consultar Exportação
@app.get(
    "/exportacao/{produto}/{ano}",
    tags=["Rotas de Web Scrapper"],
    summary="Consultar Exportação",
    description="Retorna dados de exportação vitivinícola para o produto e ano especificados.",
    responses={
        200: {"description": "Dados de exportação retornados com sucesso."},
        400: {"description": "Produto de exportação inválido."},
        401: {"description": "Usuário não autenticado."},
        404: {"description": "Dados não encontrados para o produto e ano especificados."},
        500: {"description": "Erro interno do servidor."}
    }
)
def get_exportacao(
    produto: ExportacaoTipo = Path(
    ...,
    description="Tipo de exportação vitivinícola. Opções válidas:\n"
                "- `subopt_01`: Vinhos de Mesa\n"
                "- `subopt_02`: Espumantes\n"
                "- `subopt_03`: Uvas Frescas\n"
                "- `subopt_04`: Suco de Uva"
    ),
    ano: int = Path(
        ...,
        ge=1970,
        le=2023,
        description="Ano da consulta (entre 1970 e 2023)."
    ),
    current_user: User = Depends(get_current_user)
) -> list:
    """
    Endpoint para consultar dados de exportação vitivinícola.
    Tenta raspar os dados do site da Embrapa; em caso de falha, usa um arquivo CSV local.
    """
    tipo_to_filename = {
        "subopt_01": "ExpVinho.csv",
        "subopt_02": "ExpEspumantes.csv",
        "subopt_03": "ExpUva.csv",
        "subopt_04": "ExpSuco.csv"
    }

    if produto not in tipo_to_filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Produto '{produto}' inválido.")

    try:
        data = scrape_embrapa(ano, "opt_06", produto)
        if data:
            return data
        else:
            raise ValueError("Web scraping não retornou dados, tentando fallback para CSV.")
    except Exception as e:
        df_columns_map = {"País": "pais", str(ano): "quantidade", f"{ano}.1": "valor_usd"}
        return get_data_from_csv_fallback(tipo_to_filename[produto], ano, df_columns_map, sep="\t")
