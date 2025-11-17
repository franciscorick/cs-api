# Documentação de Testes - API Flask CS

Esta documentação contém comandos `curl` para testar todas as rotas da API.

## Configuração

- **URL Local:** `http://localhost:5001`
- **URL Produção (Vercel):** Substitua `localhost:5001` pela URL da sua aplicação

---

## 📋 Rotas Disponíveis

### 1. **GET /** - Rota Principal
Retorna informações básicas sobre a API.

```bash
curl http://localhost:5001/
```

**Resposta esperada (200):**
```json
{
  "mensagem": "API Flask ativa na Vercel",
  "status": "ok",
  "endpoints": ["/", "/estatisticas"],
  "versao": "1.0.0"
}
```

---

### 2. **GET /estatisticas** - Listar Todas as Estatísticas
Retorna todas as estatísticas armazenadas no banco de dados.

```bash
curl http://localhost:5001/estatisticas
```

**Resposta esperada (200):**
```json
[
  {
    "id": 1,
    "nome": "Jogador1",
    "abates": 10,
    "mortes": 5,
    "assistencias": 8,
    "dano": 2500,
    "data": "2025-11-01",
    "dinheiro": 3500
  },
  {
    "id": 2,
    "nome": "Jogador2",
    "abates": 12,
    "mortes": 3,
    "assistencias": 6,
    "dano": 3200,
    "data": "2025-11-02",
    "dinheiro": 4100
  }
]
```

---

### 3. **POST /estatisticas** - Criar Nova Estatística
Adiciona uma nova estatística ao banco de dados.

```bash
curl -X POST http://localhost:5001/estatisticas \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "NovoJogador",
    "abates": 8,
    "mortes": 4,
    "assistencias": 6,
    "dano": 1800,
    "data": "2025-11-10",
    "dinheiro": 2500
  }'
```

**Resposta esperada (201):**
```json
{
  "id": 5,
  "nome": "NovoJogador",
  "abates": 8,
  "mortes": 4,
  "assistencias": 6,
  "dano": 1800,
  "data": "2025-11-10",
  "dinheiro": 2500
}
```

**Erro - Campos faltando (400):**
```bash
curl -X POST http://localhost:5001/estatisticas \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "SemCampos"
  }'
```

**Erro - Tipos inválidos (400):**
```bash
curl -X POST http://localhost:5001/estatisticas \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "Teste",
    "abates": "texto_invalido",
    "mortes": 1,
    "assistencias": 1,
    "dano": 100,
    "data": "2025-11-10",
    "dinheiro": 100
  }'
```

---

### 4. **PUT /estatistica/<id>** - Atualizar Estatística
Atualiza uma estatística existente pelo ID.

```bash
curl -X PUT http://localhost:5001/estatistica/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "JogadorAtualizado",
    "abates": 15,
    "mortes": 2,
    "assistencias": 10,
    "dano": 3500,
    "data": "2025-11-10",
    "dinheiro": 5200
  }'
```

**Resposta esperada (200):**
```json
{
  "id": 1,
  "nome": "JogadorAtualizado",
  "abates": 15,
  "mortes": 2,
  "assistencias": 10,
  "dano": 3500,
  "data": "2025-11-10",
  "dinheiro": 5200
}
```

**Erro - ID não encontrado (404):**
```bash
curl -X PUT http://localhost:5001/estatistica/9999 \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "Teste",
    "abates": 1,
    "mortes": 1,
    "assistencias": 1,
    "dano": 100,
    "data": "2025-11-10",
    "dinheiro": 100
  }'
```

---

### 5. **DELETE /estatistica/<id>** - Deletar Estatística
Remove uma estatística do banco de dados pelo ID.

```bash
curl -X DELETE http://localhost:5001/estatistica/5
```

**Resposta esperada (200):**
```json
{
  "mensagem": "Estatística deletada com sucesso."
}
```

**Erro - ID não encontrado (404):**
```bash
curl -X DELETE http://localhost:5001/estatistica/9999
```

**Resposta:**
```json
{
  "erro": "Estatística não encontrada."
}
```

---

### 6. **GET /logs** - Visualizar Logs
Retorna todos os eventos registrados no sistema.

```bash
curl http://localhost:5001/logs
```

**Resposta esperada (200):**
```json
[
  {
    "evento": "inicializa_banco",
    "descricao": "banco foi inicializado",
    "timestamp": "2025-11-10 14:30:25"
  },
  {
    "evento": "acessa_rota",
    "descricao": "rota estatistica foi acessada",
    "timestamp": "2025-11-10 14:32:10"
  },
  {
    "evento": "cria_estatistica",
    "descricao": "estatistica criada id=5",
    "timestamp": "2025-11-10 14:35:42"
  },
  {
    "evento": "atualiza_estatistica",
    "descricao": "estatistica atualizada id=1",
    "timestamp": "2025-11-10 14:38:15"
  },
  {
    "evento": "deleta_estatistica",
    "descricao": "estatistica deletada id=5",
    "timestamp": "2025-11-10 14:40:03"
  }
]
```

---

## 🔄 Fluxo Completo de Teste (CRUD)

Execute os comandos abaixo em sequência para testar todas as operações:

```bash
# 1. Verificar que a API está ativa
curl http://localhost:5001/

# 2. Listar todas as estatísticas iniciais
curl http://localhost:5001/estatisticas

# 3. Criar uma nova estatística
curl -X POST http://localhost:5001/estatisticas \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "TesteCompleto",
    "abates": 20,
    "mortes": 5,
    "assistencias": 12,
    "dano": 4500,
    "data": "2025-11-10",
    "dinheiro": 6000
  }'

# 4. Listar novamente (deve incluir a nova estatística)
curl http://localhost:5001/estatisticas

# 5. Atualizar a estatística criada (use o ID retornado no passo 3)
curl -X PUT http://localhost:5001/estatistica/5 \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "TesteAtualizado",
    "abates": 25,
    "mortes": 3,
    "assistencias": 15,
    "dano": 5500,
    "data": "2025-11-10",
    "dinheiro": 7500
  }'

# 6. Verificar a atualização
curl http://localhost:5001/estatisticas

# 7. Deletar a estatística
curl -X DELETE http://localhost:5001/estatistica/5

# 8. Confirmar exclusão
curl http://localhost:5001/estatisticas

# 9. Visualizar todos os logs de eventos
curl http://localhost:5001/logs
```

---

## 📊 Campos Obrigatórios

Ao criar ou atualizar uma estatística, todos os campos abaixo são **obrigatórios**:

| Campo          | Tipo    | Descrição                           |
|----------------|---------|-------------------------------------|
| `nome`         | string  | Nome do jogador                     |
| `abates`       | integer | Número de abates (kills)            |
| `mortes`       | integer | Número de mortes                    |
| `assistencias` | integer | Número de assistências              |
| `dano`         | integer | Dano total causado                  |
| `data`         | string  | Data da estatística (YYYY-MM-DD)    |
| `dinheiro`     | integer | Quantidade de dinheiro acumulada    |

---

## 🚀 Iniciando o Servidor Local

Para testar localmente, execute:

```bash
python api/index.py
```

O servidor estará disponível em `http://localhost:5001`

---

## 📝 Notas

- Todos os endpoints retornam JSON
- Em caso de erro, a API retorna um objeto com a chave `"erro"` e uma mensagem descritiva
- Os logs são salvos automaticamente no arquivo `logs/log.csv`
- O banco de dados SQLite é criado automaticamente na primeira execução
- Na Vercel, o banco é efêmero (armazenado em `/tmp/`)
