from typing import Optional 
import os
import pandas as pd
from config import CSV_FOLDER

# Função auxiliar para lidar com o fallback para CSV
def get_data_from_csv_fallback(
    csv_filename: str,
    ano: int,
    df_columns_map: dict, # Mapeamento de colunas do CSV para nomes de retorno
    sep: str = ";",
    filter_col: Optional[str] = None, # Coluna para filtrar (ex., 'Produto', 'cultivar')
    filter_val: Optional[str] = None # Valor para filtrar
) -> list:
    """
    Tenta ler dados de um arquivo CSV local como fallback.

    Args:
        csv_filename (str): Nome do arquivo CSV.
        ano (int): Ano para filtrar os dados.
        df_columns_map (dict): Mapeamento de colunas do CSV para nomes de retorno.
        sep (str): Separador do CSV.
        filter_col (Optional[str]): Nome da coluna para aplicar filtro adicional.
        filter_val (Optional[str]): Valor para o filtro adicional.

    Returns:
        list: Lista de dicionários com os dados filtrados.

    Raises:
        HTTPException: Se o arquivo CSV não for encontrado ou dados para o ano/filtro não existirem.
    """
    csv_path = os.path.join(CSV_FOLDER, csv_filename)

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dados não encontrados no site nem no arquivo CSV: {csv_filename}.")

    df = pd.read_csv(csv_path, sep=sep)
    year_column = str(ano)

    # Verifica se as colunas necessárias existem no DataFrame
    required_columns = list(df_columns_map.keys())
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Colunas necessárias não encontradas no CSV para o ano {ano}.")

    # Filtra por ano e renomeia colunas
    filtered_df = df[required_columns].rename(columns=df_columns_map)

    # Aplica filtro adicional se especificado
    if filter_col and filter_val:
        if filter_col not in filtered_df.columns:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Coluna de filtro '{filter_col}' não encontrada no CSV.")
        filtered_df = filtered_df[filtered_df[filter_col] == filter_val]

    result = filtered_df.to_dict(orient="records")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Nenhum dado encontrado para o ano {ano} e/ou filtro especificado.")

    return result
