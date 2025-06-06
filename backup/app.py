# Se o site estiver instável, usar dados locais (CSV/JSON pré-baixados).
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_embrapa(ano: int, opcao: str, subopcao: str = None):
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao={opcao}"
    if subopcao:
        url += f"&subopcao={subopcao}"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela = soup.find("table", {"class": "tb_base tb_dados"}) 
        linhas = tabela.find_all("tr")

        # Pegar cabeçalhos da primeira linha
        cabecalhos_linha = linhas[0].find_all("th")
        cabecalhos = [th.get_text(strip=True) for th in cabecalhos_linha]

        # Verificar número de colunas pelos cabeçalhos
        num_colunas = len(cabecalhos)

        # Criar dicionário apropriado baseado no número de colunas
        resultado = {}

        # Itera sobre as linhas para extrair os dados
        for linha in linhas[1:]:
            celulas = linha.find_all("td")
            if celulas:  # Ignora linhas sem células
                valores = [td.get_text(strip=True) for td in celulas]
                
                # Trata o caso de 2 colunas (Produto/Quantidade)
                if num_colunas == 2:
                    # Usa a primeira coluna como chave e a segunda como valor
                    if len(valores) >= 2:
                        resultado[valores[0]] = valores[1]
                
                # Trata o caso de 3 colunas (País/Quantidade/Valor)
                elif num_colunas == 3:
                    # Usa a primeira coluna como chave e cria um sub-dicionário para as outras colunas
                    if len(valores) >= 3:
                        resultado[valores[0]] = {
                            cabecalhos[1]: valores[1],
                            cabecalhos[2]: valores[2]
                        }
        
        return resultado
    
    except Exception as e:
        print(f"Erro ao fazer scraping: {e}")
        return {}
    
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer

app = FastAPI()
security = HTTPBearer()

# --- Autenticação (Opcional) ---
@app.post("/login")
def login(username: str, password: str):
    # Lógica JWT (exemplo simplificado)
    return {"token": "TOKEN_JWT_AQUI"}

# --- Endpoints Principais ---
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


