from flask import Flask, jsonify
import sqlite3
import os
import csv
import time

app = Flask(__name__)

def log_event(evento, descricao):
    log_caminho = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'log.csv')
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
		"endpoints": ["/", "/estatisticas"],
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
    return jsonify({
        "mensagem": "post funcional"
    })


# Inicializa o DB na primeira execução
init_db()

if __name__ == '__main__':
	# Executa a aplicação em modo debug
  app.run(host='0.0.0.0', port=5001, debug=True)

