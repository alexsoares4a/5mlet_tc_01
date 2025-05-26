# 🍷 Tech Challenge - Fase 1 - Machine Learning Engineering

## 🧾 Descrição do Projeto

Este projeto faz parte do Tech Challenge - Fase 1 do curso de Pós-Tech em Machine Learning Engineering da **Faculdade de Informática e Administração Paulista - FIAP**. O objetivo é criar uma **API REST pública** capaz de consultar dados de vitivinicultura diretamente do site da **EMBRAPA**, incluindo as seguintes categorias:
- Produção
- Processamento
- Comercialização
- Importação
- Exportação


## 🧩 Tecnologias Utilizadas

| Componente | Tecnologia | Motivação |
|-----------|------------|-----------|
| API REST | FastAPI | Validação automática, documentação integrada |
| Autenticação | JWT | Segurança nas rotas protegidas |
| Banco de dados | SQLite | Leve e rápido para MVP |
| Web Scraping | BeautifulSoup | Extração simples e eficiente |
| Fallback local | CSV | Garante disponibilidade mesmo offline |
| Front-end | Bootstrap | Interface clara e responsiva |
| Deploy | Render | Gratuito, fácil de usar e compatível com FastAPI |
---

## 🛠️ Como Rodar a Aplicação

### 🔧 Requisitos

- Python 3.12.1
- pip
- Banco de dados SQLite (já incluso)
- Ambiente virtual recomendado (`venv`)

### 📦 Passo a passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/alexsoares4a/5mlet_tc_01.git
   cd 5mlet_tc_01
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Linux/Mac
   venv\Scripts\activate     # No Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**

   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```env
   SECRET_KEY=sua_chave_secreta
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

5. **Inicie a API**
   ```bash
   uvicorn app:app --reload
   ```

6. **Acesse a documentação interativa**
   ```
   http://localhost:8000/docs
   ```

---

## 🧪 Como Testar os Endpoints

Você pode testar os endpoints diretamente pela interface Swagger (recomendado) ou por ferramentas como Postman ou curl.

A documentação e o passo a passo para os testes estão descritos na página a seguir:
- [Documentação da API (Site)](https://fivemlet-tc-01.onrender.com/static/page-documentacao.html)


---

## 📁 Estrutura de Pastas e Módulos

```
tech-challenge/
├── auth/
│   ├── auth.py          # Funções de autenticação (JWT)
│   └── schemas.py       # Modelos Pydantic para autenticação
├── database/
│   ├── crud.py          # Operações no banco de dados
│   ├── database.py      # Configuração da conexão com SQLite
│   └── models.py        # Modelo SQLAlchemy para usuários
├── static/              # Arquivos HTML/CSS/JS/IMG estáticos
│   ├── css/
│   ├── js/
│   ├── img/
│   └── index.html       # Página inicial do front-end
├── csv/                 # Pasta com arquivos CSV para fallback
├── scraper.py           # Realiza web scraping do site da Embrapa
├── app.py               # Principal arquivo da API FastAPI
├── config.py            # Variáveis de ambiente e configurações
├── requirements.txt     # Dependências do projeto
└── .gitignore           # Arquivos ignorados pelo Git
```

---

## 📎 Recursos Úteis

- [Site de Projeto](https://fivemlet-tc-01.onrender.com)
- [Documentação da API (Swagger)](https://fivemlet-tc-01.onrender.com/docs)

---

## 📬 Contato

- Nome: Alex Soares da Silva
- LinkedIn: [alexsoares4a](https://www.linkedin.com/in/alexsoares4a/)
- E-mail: alexssonline@gmail.com
