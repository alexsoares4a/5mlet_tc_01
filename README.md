# 🍷 VitiBrasil API: Tech Challenge - Fase 1 - Machine Learning Engineering

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3121/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Render Deploy](https://img.shields.io/badge/Deploy-Render-6CC644?logo=render)](https://fivemlet-tc-01.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🧾 Descrição do Projeto

Este projeto é parte do Tech Challenge - Fase 1 do curso de Pós-Graduação em Machine Learning Engineering da **Faculdade de Informática e Administração Paulista - FIAP**.

O objetivo principal é desenvolver uma **API REST pública** capaz de consultar dados de vitivinicultura diretamente do site da **EMBRAPA**, nas seguintes categorias:
- Produção
- Processamento
- Comercialização
- Importação
- Exportação

A API foi projetada para **servir como uma fonte de dados robusta e padronizada para futuros modelos de Machine Learning**, permitindo a ingestão automatizada de informações históricas e em tempo real. Ela realiza web scraping dos dados e conta com um mecanismo de fallback local para garantir a disponibilidade mesmo em caso de instabilidade da fonte original.

## ✨ Funcionalidades Principais

*   **Web Scraping:** Coleta de dados em tempo real diretamente do site da Embrapa.
*   **API RESTful:** Endpoints claros e bem definidos para acesso aos dados em formato JSON.
*   **Autenticação JWT:** Segurança nas rotas protegidas para controle de acesso.
*   **Fallback Local:** Garante a disponibilidade dos dados mesmo com o site da Embrapa offline, utilizando arquivos CSV pré-salvos.
*   **Gerenciamento de Migrações:** Utilização do Alembic para controle de versão do esquema do banco de dados.
*   **Documentação Interativa:** Swagger UI integrado para fácil exploração e teste da API.

##  🧩 Tecnologias Utilizadas

| Componente | Tecnologia | Motivação |
|:----------|:-----------|:----------|
| API REST | FastAPI | Framework moderno, rápido, com validação automática e documentação integrada (Swagger/ReDoc). |
| ORM | SQLAlchemy | ORM flexível e robusto para interação com o banco de dados. |
| Migrações DB | Alembic | Gerenciamento de versões do esquema do banco de dados, garantindo consistência e controle. |
| Autenticação | JWT | Padrão de mercado para autenticação segura e stateless em APIs. |
| Hash de Senhas | Passlib | Biblioteca segura para criptografia e verificação de senhas. |
| Banco de Dados | SQLite | Leve, rápido e ideal para protótipos e MVPs, sem necessidade de servidor externo. |
| Web Scraping | BeautifulSoup | Ferramenta simples e eficiente para extração de dados de páginas HTML. |
| Manipulação de Dados | Pandas | Essencial para leitura, processamento e manipulação de dados, especialmente para o fallback CSV. |
| Fallback Local | CSV | Solução simples e eficaz para garantir a disponibilidade dos dados offline. |
| Front-end | Bootstrap | Framework CSS para uma interface estática, clara, responsiva e de fácil desenvolvimento. |
| Deploy | Render | Plataforma gratuita e de fácil configuração para hospedagem de aplicações FastAPI. |

---

## 🛠️ Como Rodar a Aplicação Localmente

### 🔧 Requisitos

*   Python 3.12.1 (ou superior)
*   `pip` (gerenciador de pacotes do Python)
*   Banco de dados SQLite (já incluso, não requer instalação separada)
*   Recomendado: Utilização de um ambiente virtual (`venv`)

### 📦 Passo a passo

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/alexsoares4a/5mlet_tc_01.git
    cd 5mlet_tc_01
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    python -m venv venv
    # No Linux/macOS:
    source venv/bin/activate
    # No Windows:
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente**

    Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis. **É importante que a `DATABASE_URL` aponte para o diretório `data/` para o correto funcionamento das migrações e persistência do DB.**

    ```env
    SECRET_KEY=sua_chave_secreta_muito_segura_aqui # Altere para uma chave forte e única
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    CSV_FOLDER="data/csv"
    DATABASE_URL="sqlite:///./data/embrapa.db" # Garante que o DB seja criado em 'data/'
    ```

5.  **Execute as migrações do banco de dados (Alembic)**

    Este passo cria o arquivo `embrapa.db` e a tabela `users` no diretório `data/`.
    ```bash
    alembic upgrade head
    ```

6.  **Inicie a API**
    ```bash
    uvicorn app:app --reload
    ```

7.  **Acesse a documentação interativa**
    A API estará disponível em `http://localhost:8000`.
    A documentação interativa (Swagger UI) pode ser acessada em:
    ```
    http://localhost:8000/docs
    ```

---

## 🧪 Como Testar os Endpoints

Você pode testar os endpoints diretamente pela interface Swagger (recomendado) ou por ferramentas como Postman ou `curl`.

A documentação completa e o passo a passo detalhado para os testes, incluindo o fluxo de autenticação e exemplos de requisições, estão disponíveis na página do site:
- [Documentação da API (Site)](https://fivemlet-tc-01.onrender.com/static/page-documentacao.html)

---

## 📁 Estrutura de Pastas e Módulos

```
emlet_tc_01/
├── auth/
│   ├── auth.py          # Funções de autenticação (JWT)
│   └── schemas.py       # Modelos Pydantic para autenticação
├── data/                # Arquivos de dados
│   ├── csv/             # Pasta com arquivos CSV para fallback
│   └── embrapa.db       # Banco de Dados SQLite com dados dos usuários
├── database/
│   ├── crud.py          # Operações no banco de dados
│   ├── database.py      # Configuração da conexão com SQLite
│   └── models.py        # Modelo SQLAlchemy para usuários
├── static/              # Arquivos HTML/CSS/JS/IMG estáticos (Template Bootstrap)
│   ├── css/
│   ├── js/
│   ├── img/
│   └── index.html       # Página inicial do front-end
├── schemas/
│   ├── enums.py         # Enumeradores para tipos de Processamento, Importação e Exportação
├── services/            # Lógica de negócio e utilitários
│   ├── scraper.py       # Realiza web scraping do site da Embrapa
│   └── fallback.py      # Realiza o fallback com arquivos CSV     
├── app.py               # Principal arquivo da API FastAPI
├── config.py            # Variáveis de ambiente e configurações        
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente
└── .gitignore           # Arquivos ignorados pelo Git
```

---

## 📎 Recursos Úteis

*   **Site do Projeto:** [https://fivemlet-tc-01.onrender.com](https://fivemlet-tc-01.onrender.com)
*   **Documentação da API (Swagger UI):** [https://fivemlet-tc-01.onrender.com/docs](https://fivemlet-tc-01.onrender.com/docs)


---

## 📬 Contato

*   **Nome:** Alex Soares da Silva
*   **LinkedIn:** [alexsoares4a](https://www.linkedin.com/in/alexsoares4a/)
*   **E-mail:** alexssonline@gmail.com

---
