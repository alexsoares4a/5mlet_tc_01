from enum import Enum

# Enum para Processamento
class ProcessamentoTipo(str, Enum):
    """
    Enumeração para os tipos de processamento de uvas.
    """
    VINIFERAS = "subopt_01"
    AMERICANAS_HIBRIDAS = "subopt_02"
    MESA = "subopt_03"
    SEM_CLASSIFICACAO = "subopt_04"

# Enum para Importação
class ImportacaoTipo(str, Enum):
    """
    Enumeração para os tipos de importação vitivinícola.
    """
    VINHOS_MESA = "subopt_01"
    ESPUMANTES = "subopt_02"
    UVAS_FRESCAS = "subopt_03"
    UVAS_PASSAS = "subopt_04"
    SUCO_UVA = "subopt_05"

# Enum para Exportação
class ExportacaoTipo(str, Enum):
    """
    Enumeração para os tipos de exportação vitivinícola.
    """
    VINHOS_MESA = "subopt_01"
    ESPUMANTES = "subopt_02"
    UVAS_FRESCAS = "subopt_03"
    SUCO_UVA = "subopt_04"
