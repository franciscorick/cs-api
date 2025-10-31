# CS API - Counter-Strike Statistics API

API Flask para gerenciar estatísticas de jogadores de Counter-Strike.

## 🚀 Deploy na Vercel

### Pré-requisitos
1. Conta na [Vercel](https://vercel.com)
2. [Vercel CLI](https://vercel.com/cli) instalado (opcional)

### Deploy via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer login
vercel login

# Deploy
vercel
```

### Deploy via GitHub

1. Faça push do código para o GitHub
2. Acesse [vercel.com](https://vercel.com)
3. Importe o repositório
4. A Vercel detectará automaticamente o projeto Flask

## 📋 Endpoints

- `GET /` - Status da API
- `GET /estatisticas` - Lista todas as estatísticas
- `POST /estatisticas` - Adiciona nova estatística
- `GET /logs` - Lista logs de eventos

## ⚠️ Importante - Banco de Dados

Na Vercel, o SQLite funciona em `/tmp` e **é temporário**. Os dados são perdidos entre deployments.

### Soluções para persistência:
1. **Vercel Postgres** (recomendado para produção)
2. **Supabase** (PostgreSQL gratuito)
3. **PlanetScale** (MySQL serverless)
4. **MongoDB Atlas** (NoSQL)

## 🛠️ Desenvolvimento Local

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd cs-api

# Instalar dependências
pip install -r requirements.txt
```

### Executar a API

```bash
# Rodar localmente
python run.py
```

A API estará disponível em: http://localhost:5001

### Testando os endpoints

```bash
# GET - Listar estatísticas
curl http://localhost:5001/estatisticas

# POST - Adicionar nova estatística
curl -X POST http://localhost:5001/estatisticas \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "jogador1",
    "abates": 15,
    "mortes": 10,
    "assistencias": 5,
    "dano": 2500,
    "data": "2025-10-31",
    "dinheiro": 3000
  }'

# GET - Ver logs
curl http://localhost:5001/logs
```

## 📦 Estrutura do Projeto

```
cs-api/
├── api/
│   ├── __init__.py      # Pacote API
│   └── index.py         # Rotas da API (controllers)
├── utils/
│   ├── __init__.py      # Pacote Utils
│   ├── database.py      # Funções de banco de dados
│   ├── logger.py        # Sistema de logging
│   └── estatisticas.py  # Modelo de dados Estatisticas
├── data/
│   └── estatisticas.csv # Dados iniciais
├── logs/
│   └── log.csv          # Arquivo de logs (gerado automaticamente)
├── run.py               # Script para executar localmente
├── requirements.txt     # Dependências Python
├── vercel.json          # Configuração Vercel
└── .vercelignore        # Arquivos ignorados no deploy
```

### Arquitetura

O projeto segue uma arquitetura em camadas com separação de responsabilidades:

- **`api/`**: Camada de apresentação (rotas/endpoints)
- **`utils/`**: Camada de lógica de negócio e utilitários
  - `database.py`: Gerenciamento do banco SQLite
  - `logger.py`: Sistema de logging de eventos
  - `estatisticas.py`: Modelo de dados com métodos de negócio

### Banco de Dados

- **Local**: SQLite (`estatisticas.db` na raiz do projeto)
- **Vercel**: SQLite em `/tmp` (temporário, dados perdidos entre deploys)
