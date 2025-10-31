from flask import Flask, jsonify, request
import sqlite3
import os
import csv
import time

app = Flask(__name__)

def get_logs_path():
    return os.path.join('/tmp', 'log.csv')  # Mude o caminho para /tmp

def log_event(evento, descricao):
    log_caminho = get_logs_path()
    with open(log_caminho, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{evento},{descricao},{int(time.time())}\n")

def get_db():
    """Conecta ao banco de dados SQLite."""
    # Na Vercel, use /tmp para arquivos temporários
    db_path = '/tmp/estatisticas.db' if os.environ.get('VERCEL') else 'estatisticas.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria tabelas e popula dados iniciais se necessário."""
    db = get_db()
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
    db.commit()

    # Popular dados iniciais apenas se vazio
    cur = db.execute("SELECT COUNT(*) AS total FROM estatisticas")
    total = cur.fetchone()[0]
    if total == 0:
        # Ler dados do arquivo CSV
        arquivo_dados_estatisticos = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'estatisticas.csv')
        estatisticas_iniciais = []

        with open(arquivo_dados_estatisticos, 'r', encoding='utf-8') as arquivo_csv:
            leitor = csv.DictReader(arquivo_csv)
            for linha in leitor:
                estatisticas_iniciais.append((
                    linha['nome'],
                    int(linha['abates']),
                    int(linha['mortes']),
                    int(linha['assistencias']),
                    int(linha['dano']),
                    linha['data'],
                    int(linha['dinheiro'])
                ))

        db.executemany(
            "INSERT INTO estatisticas (nome, abates, mortes, assistencias, dano, data, dinheiro) VALUES (?, ?, ?, ?, ?, ?, ?)",
            estatisticas_iniciais
        )
        db.commit()
    db.close()

    log_event('inicializa_banco', 'banco foi inicializado')

class Estatisticas:
    def __init__(self, nome, abates, mortes, assistencias, dano, data, dinheiro): #construtor
        self.nome = nome
        self.abates = abates
        self.mortes = mortes
        self.assistencias = assistencias
        self.dano = dano
        self.data = data
        self.dinheiro = dinheiro

    def calcular_kd(self): #definição de função
        return self.abates/self.mortes

@app.route('/')
def index():
	"""Rota principal que retorna um JSON simples"""
	return jsonify({
		"mensagem": "API Flask ativa na Vercel",
		"status": "ok",
		"endpoints": [
            "/",
            "/estatisticas",
            "/logs"
        ],
		"versao": "1.0.0"
	})

@app.route('/estatisticas')
def buscar_estatisticas():
    db = get_db()
    try:
        registros = db.execute(
            "SELECT id, nome, abates, mortes, assistencias, dano, data, dinheiro FROM estatisticas ORDER BY id"
        )
        linhas = registros.fetchall() #fetchall = traz os dados da consulta
        estatisticas = []
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
        log_event('acessa_rota', 'rota estatistica foi acessada')
        return jsonify(estatisticas)
    finally:
        db.close()

@app.route('/estatisticas', methods=['POST'])
def posta_estatistica():
    db = get_db()
    try:
        dados = request.get_json()

        # Validar campos obrigatórios
        campos_obrigatorios = ['nome', 'abates', 'mortes', 'assistencias', 'dano', 'data', 'dinheiro']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

        # Inserir nova estatística
        db.execute(
            "INSERT INTO estatisticas (nome, abates, mortes, assistencias, dano, data, dinheiro) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (dados['nome'], dados['abates'], dados['mortes'], dados['assistencias'], dados['dano'], dados['data'], dados['dinheiro'])
        )
        db.commit()

        # Recuperar o ID da estatística inserida
        novo_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        log_event('adiciona_estatistica', f'nova estatistica adicionada: {dados["nome"]}')

        return jsonify({
            "mensagem": "Estatística adicionada com sucesso",
            "id": novo_id
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()

@app.route('/logs')
def buscar_logs():
    log_path = get_logs_path()
    logs = []
    with open(log_path, 'r', encoding='utf-8') as log_file:
        leitor = csv.DictReader(log_file)
        logs = [
            {
                "evento": linha["evento"],
                "descricao": linha["descricao"],
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(linha["timestamp"])))
            }
            for linha in leitor  # ← Funcional (declarativo)
        ]
    return jsonify(logs)

@app.route('/env')
def mostrar_env():
    """Rota para mostrar variáveis de ambiente (para debug)"""
    env_vars = {key: os.environ[key] for key in os.environ}
    return jsonify(env_vars)

# Inicializa o DB na primeira execução
init_db()

if __name__ == '__main__':
	# Executa a aplicação em modo debug
  app.run(host='0.0.0.0', port=5001, debug=True)

