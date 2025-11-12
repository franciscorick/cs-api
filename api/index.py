# Importa as bibliotecas necessárias
from flask import Flask, jsonify, request    # Flask = framework para criar APIs web / jsonify = retorna dados em formato JSON.
from flask_cors import CORS  # Habilita CORS para permitir requisições de outros domínios
import sqlite3      # Banco de dados leve (SQLite).
import os       # Manipulação de diretórios e caminhos de arquivo.
import csv      # Leitura e escrita de arquivos CSV.
import time     # Usado para gerar timestamps (tempo atual em segundos).

# Inicializa o app Flask
app = Flask(__name__)

# Configura CORS para permitir requisições de qualquer origem
# Em produção, considere restringir para domínios específicos
CORS(app, resources={r"/*": {"origins": "*"}})

# --------------------------- UTILIDADE DE LOG PATH ---------------------------
def get_log_path():
    """Retorna o caminho do arquivo de log.
    Em ambiente Vercel, usa /tmp (único local com escrita permitida).
    """
    if os.environ.get('VERCEL'):
        return '/tmp/log.csv'
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'log.csv')

def ensure_log_file():
    """Garante que o arquivo de log exista e tenha cabeçalho."""
    caminho = get_log_path()
    pasta = os.path.dirname(caminho)
    try:
        os.makedirs(pasta, exist_ok=True)
        if not os.path.exists(caminho):
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write('evento,descricao,timestamp\n')
    except Exception:
        # Não falha a função caso logging não esteja disponível
        pass

# --------------------------- FUNÇÃO DE LOG ---------------------------
def log_event(evento, descricao):
    """Registra um evento no arquivo de log de forma resiliente."""
    try:
        ensure_log_file()
        log_caminho = get_log_path()
        with open(log_caminho, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{evento},{descricao},{int(time.time())}\n")
    except Exception:
        # Em ambientes sem permissão de escrita, apenas ignora o log
        pass

# --------------------------- CONEXÃO COM O BANCO ---------------------------
def get_db():
    """Conecta ao banco de dados SQLite."""
    # Se estiver rodando na Vercel, usa /tmp para arquivos temporários (único local com permissão de escrita).
    db_path = '/tmp/estatisticas.db' if os.environ.get('VERCEL') else 'estatisticas.db'
     # Conecta ao banco.
    conn = sqlite3.connect(db_path)
     # Faz com que as linhas retornadas sejam acessadas como dicionários.
    conn.row_factory = sqlite3.Row
    return conn

 # --------------------------- INICIALIZAÇÃO DO BANCO ---------------------------
def init_db():
    """Cria tabelas e popula dados iniciais se necessário."""
    db = get_db()
    # Cria a tabela se ainda não existir
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS estatisticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            abates INTEGER NOT NULL,
            mortes INTEGER NOT NULL,
            assistencias INTEGER NOT NULL,
            dano INTEGER NOT NULL,
            data TEXT NOT NULL,
            dinheiro INTEGER NOT NULL
        )
        """
    )
    db.commit() # Confirma a criação da tabela

    # Verifica se a tabela está vazia
    cur = db.execute("SELECT COUNT(*) AS total FROM estatisticas")
    total = cur.fetchone()[0]
    if total == 0:
        # Se estiver vazia, lê o arquivo CSV inicial e popula a tabela.
        arquivo_dados_estatisticos = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'estatisticas.csv')
        estatisticas_iniciais = []

         # Abre o CSV com os dados de exemplo
        with open(arquivo_dados_estatisticos, 'r', encoding='utf-8') as arquivo_csv:
            leitor = csv.DictReader(arquivo_csv)
            for linha in leitor:
                 # Cria uma tupla com os dados convertidos
                estatisticas_iniciais.append((
                    linha['nome'],
                    int(linha['abates']),
                    int(linha['mortes']),
                    int(linha['assistencias']),
                    int(linha['dano']),
                    linha['data'],
                    int(linha['dinheiro'])
                ))

         # Insere todos os registros no banco
        db.executemany(
            "INSERT INTO estatisticas (nome, abates, mortes, assistencias, dano, data, dinheiro) VALUES (?, ?, ?, ?, ?, ?, ?)",
            estatisticas_iniciais
        )
        db.commit()     # Salva as inserções
    db.close()  # Fecha a conexão com o banco

     # Registra o evento no log
    log_event('inicializa_banco', 'banco foi inicializado')

 # --------------------------- CLASSE ESTATISTICAS ---------------------------
class Estatisticas:
    # Construtor: define os atributos que cada estatística terá
    def __init__(self, nome, abates, mortes, assistencias, dano, data, dinheiro): #construtor
        self.nome = nome
        self.abates = abates
        self.mortes = mortes
        self.assistencias = assistencias
        self.dano = dano
        self.data = data
        self.dinheiro = dinheiro

     # Método que calcula a razão K/D (abates divididos por mortes)
    def calcular_kd(self): #definição de função
        return self.abates/self.mortes

 # --------------------------- ROTAS FLASK ---------------------------
 # Rota principal ("/")

@app.route('/')
def index():
    """Rota principal que retorna um JSON simples"""
    return jsonify({
        "mensagem": "API Flask ativa na Vercel",
        "status": "ok",
        "endpoints": [
            "/",
            "GET /estatisticas",
            "POST /estatisticas",
            "PUT /estatistica/<int:estatistica_id>",
            "DELETE /estatistica/<int:estatistica_id>",
            "GET /logs"
        ],
        "versao": "1.0.0"
    })

 # Rota "/estatisticas" (GET) → retorna os dados do banco

@app.route('/estatisticas')
def buscar_estatisticas():
    db = get_db()
    try:
         # Executa a consulta para buscar todas as estatísticas
        registros = db.execute(
            "SELECT id, nome, abates, mortes, assistencias, dano, data, dinheiro FROM estatisticas ORDER BY id"
        )
         # fetchall() = retorna todas as linhas da consulta
        linhas = registros.fetchall() #fetchall = traz os dados da consulta
         # Lista onde os dados formatados serão guardados
        estatisticas = []
         # Loop para transformar cada linha em dicionário
        for linha in linhas:
            estatisticas.append({
                "id": linha["id"],
                "nome": linha["nome"],
                "abates": linha["abates"],
                "mortes": linha["mortes"],
                "assistencias": linha["assistencias"],
                "dano": linha["dano"],
                "data": linha["data"],
                "dinheiro": linha["dinheiro"],
            })
         # Registra o acesso no log
        log_event('acessa_rota', 'rota estatistica foi acessada')
         # Retorna o JSON com a lista de estatísticas
        return jsonify(estatisticas)
    finally:
         # Fecha a conexão com o banco, independente de sucesso/erro
        db.close()

 # Rota "/estatisticas" (POST) → usada para adicionar dados (ainda não implementada)

@app.route('/estatisticas', methods=['POST'])
def posta_estatistica():
    # Tenta obter o corpo como JSON; se vier como form-data, faz fallback
    payload = request.get_json(silent=True) or request.form

    if not payload:
        return jsonify({
            "erro": "Corpo da requisição ausente ou inválido. Envie JSON com os campos obrigatórios."
        }), 400

    # Campos esperados
    campos_obrigatorios = [
        "nome", "abates", "mortes", "assistencias", "dano", "data", "dinheiro"
    ]

    faltando = [c for c in campos_obrigatorios if c not in payload]
    if faltando:
        return jsonify({
            "erro": "Campos obrigatórios ausentes",
            "faltando": faltando
        }), 400

    # Validação e conversões de tipo
    try:
        nome = str(payload["nome"]).strip()
        abates = int(payload["abates"])  # ints
        mortes = int(payload["mortes"])  # ints
        assistencias = int(payload["assistencias"])  # ints
        dano = int(payload["dano"])  # ints
        data_val = str(payload["data"]).strip()  # manter como string (YYYY-MM-DD, por ex.)
        dinheiro = int(payload["dinheiro"])  # ints
    except (ValueError, TypeError):
        return jsonify({
            "erro": "Tipos inválidos. Certifique-se de enviar inteiros para abates, mortes, assistencias, dano e dinheiro."
        }), 400

    if not nome:
        return jsonify({"erro": "'nome' não pode ser vazio."}), 400

    db = get_db()
    try:
        cur = db.execute(
            """
            INSERT INTO estatisticas (nome, abates, mortes, assistencias, dano, data, dinheiro)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (nome, abates, mortes, assistencias, dano, data_val, dinheiro)
        )
        db.commit()
        novo_id = cur.lastrowid

        # Log do evento de criação
        log_event('cria_estatistica', f'estatistica criada id={novo_id}')

        return jsonify({
            "id": novo_id,
            "nome": nome,
            "abates": abates,
            "mortes": mortes,
            "assistencias": assistencias,
            "dano": dano,
            "data": data_val,
            "dinheiro": dinheiro
        }), 201
    except Exception:
        # Em produção, evitar expor detalhes do erro
        return jsonify({"erro": "Falha ao inserir no banco de dados."}), 500
    finally:
        db.close()

@app.route('/estatistica/<int:estatistica_id>', methods=['DELETE'])
def deletar_estatistica(estatistica_id):
    db = get_db()
    try:
        cur = db.execute(
            "DELETE FROM estatisticas WHERE id = ?",
            (estatistica_id,)
        )
        db.commit()

        if cur.rowcount == 0:
            return jsonify({"erro": "Estatística não encontrada."}), 404

        # Log do evento de exclusão
        log_event('deleta_estatistica', f'estatistica deletada id={estatistica_id}')

        return jsonify({"mensagem": "Estatística deletada com sucesso."}), 200
    except Exception:
        return jsonify({"erro": "Falha ao deletar do banco de dados."}), 500
    finally:
        db.close()

@app.route('/estatistica/<int:estatistica_id>', methods=['PUT'])
def atualizar_estatistica(estatistica_id):
    payload = request.get_json(silent=True) or request.form

    if not payload:
        return jsonify({
            "erro": "Corpo da requisição ausente ou inválido. Envie JSON com os campos obrigatórios."
        }), 400

    campos_obrigatorios = [
        "nome", "abates", "mortes", "assistencias", "dano", "data", "dinheiro"
    ]

    faltando = [c for c in campos_obrigatorios if c not in payload]
    if faltando:
        return jsonify({
            "erro": "Campos obrigatórios ausentes",
            "faltando": faltando
        }), 400

    try:
        nome = str(payload["nome"]).strip()
        abates = int(payload["abates"])
        mortes = int(payload["mortes"])
        assistencias = int(payload["assistencias"])
        dano = int(payload["dano"])
        data_val = str(payload["data"]).strip()
        dinheiro = int(payload["dinheiro"])
    except (ValueError, TypeError):
        return jsonify({
            "erro": "Tipos inválidos. Certifique-se de enviar inteiros para abates, mortes, assistencias, dano e dinheiro."
        }), 400

    if not nome:
        return jsonify({"erro": "'nome' não pode ser vazio."}), 400

    db = get_db()
    try:
        cur = db.execute(
            """
            UPDATE estatisticas
            SET nome = ?, abates = ?, mortes = ?, assistencias = ?, dano = ?, data = ?, dinheiro = ?
            WHERE id = ?
            """,
            (nome, abates, mortes, assistencias, dano, data_val, dinheiro, estatistica_id)
        )
        db.commit()

        if cur.rowcount == 0:
            return jsonify({"erro": "Estatística não encontrada."}), 404

        log_event('atualiza_estatistica', f'estatistica atualizada id={estatistica_id}')

        return jsonify({
            "id": estatistica_id,
            "nome": nome,
            "abates": abates,
            "mortes": mortes,
            "assistencias": assistencias,
            "dano": dano,
            "data": data_val,
            "dinheiro": dinheiro
        }), 200
    except Exception as e:
        return jsonify({"erro": "Falha ao atualizar estatística."}), 500
    finally:
        db.close()

 # Rota "/logs" → lê e retorna o conteúdo do arquivo de logs
@app.route('/logs')
def buscar_logs():
    """Lê e retorna o conteúdo do arquivo de logs em JSON."""
    try:
        ensure_log_file()
        log_path = get_log_path()
        logs = []
        with open(log_path, 'r', encoding='utf-8') as log_file:
            leitor = csv.DictReader(log_file)
            for linha in leitor:
                try:
                    logs.append({
                        "evento": linha.get("evento", ""),
                        "descricao": linha.get("descricao", ""),
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(linha.get("timestamp") or 0)))
                    })
                except Exception:
                    # Ignora linhas malformadas
                    continue
        return jsonify(logs)
    except FileNotFoundError:
        return jsonify([])

# --------------------------- EXECUÇÃO PRINCIPAL ---------------------------
# Inicializa o banco na primeira execução do script
init_db()

 # Só executa o servidor se o arquivo for executado diretamente (não importado)
if __name__ == '__main__':
	# Roda o servidor Flask em modo debug, acessível em todas as interfaces (0.0.0.0)
  app.run(host='0.0.0.0', port=5001, debug=True)

