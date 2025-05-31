import requests
from bs4 import BeautifulSoup

def scrape_embrapa(ano: int, opcao: str, subopcao: str = None):
    """
    Realiza o web scraping de dados de vitivinicultura da Embrapa usando requests e BeautifulSoup.
    Extrai tabelas HTML e padroniza as colunas, tratando valores numéricos para serialização JSON.

    Args:
        ano (int): O ano para o qual os dados devem ser consultados.
        opcao (str): A opção principal de consulta disponível em todas as rotas.
        subopcao (str, optional): A subopção de consulta disponível para as rotas de processamento, importação e exportação.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma linha da tabela
              com chaves padronizadas ('produto', 'quantidade' ou 'pais', 'quantidade', 'valor_usd').
              Valores numéricos inválidos serão None.
              Retorna uma lista vazia em caso de erro ou se nenhuma tabela for encontrada.
    """
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao={opcao}"
    if subopcao:
        url += f"&subopcao={subopcao}"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela = soup.find("table", {"class": "tb_base tb_dados"}) 
        linhas = tabela.find_all("tr")

        # Pega os cabeçalhos da primeira linha
        cabecalhos_linha = linhas[0].find_all("th")
        cabecalhos = [th.get_text(strip=True) for th in cabecalhos_linha]

        # Verifica o número de colunas pelos cabeçalhos
        num_colunas = len(cabecalhos)

        # Cria uma lista para armazenar os resultados
        resultado = []

        # Itera sobre as linhas para extrair os dados
        for linha in linhas[1:]:
            celulas = linha.find_all("td")
            if celulas:  # Ignora linhas sem células
                valores = [td.get_text(strip=True) for td in celulas]

                # Trata o caso de 2 colunas (Produto/Quantidade)
                if num_colunas == 2:
                    resultado.append({
                        "produto": valores[0],
                        "quantidade": valores[1]
                    })

                # Trata o caso de 3 colunas (País/Quantidade/Valor)
                elif num_colunas == 3:
                    resultado.append({
                        "pais": valores[0],
                        "quantidade": valores[1],
                        "valor_usd": valores[2]
                    })

        return resultado
    
    except Exception as e:
        print(f"Erro ao fazer scraping: {e}")
        return []
