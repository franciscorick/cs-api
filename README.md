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
- `POST /estatisticas` - Adiciona nova estatística (em desenvolvimento)

## ⚠️ Importante - Banco de Dados

Na Vercel, o SQLite funciona em `/tmp` e **é temporário**. Os dados são perdidos entre deployments.

### Soluções para persistência:
1. **Vercel Postgres** (recomendado para produção)
2. **Supabase** (PostgreSQL gratuito)
3. **PlanetScale** (MySQL serverless)
4. **MongoDB Atlas** (NoSQL)

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar localmente
python main.py
```

Acesse: http://localhost:5001

## 📦 Estrutura do Projeto

```
cs-api/
├── api/
│   └── index.py      # Entry point para Vercel
├── main.py           # Aplicação Flask original
├── requirements.txt  # Dependências Python
├── vercel.json       # Configuração Vercel
└── .vercelignore     # Arquivos ignorados no deploy
```
