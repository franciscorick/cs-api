# Importa as bibliotecas necessárias
from flask import Flask, jsonify    # Flask = framework para criar APIs web / jsonify = retorna dados em formato JSON.
import sqlite3      # Banco de dados leve (SQLite).
import os       # Manipulação de diretórios e caminhos de arquivo.
import csv      # Leitura e escrita de arquivos CSV.
import time     # Usado para gerar timestamps (tempo atual em segundos).

# Inicializa o app Flask
app = Flask(__name__)

# --------------------------- FUNÇÃO DE LOG ---------------------------
def log_event(evento, descricao):
     # Monta o caminho até o arquivo de log (na pasta logs/log.csv).
    log_caminho = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'log.csv')
     # Abre o arquivo no modo 'append' (acrescentar novas linhas).
    with open(log_caminho, 'a', encoding='utf-8') as log_file: 
         # Escreve uma linha com o evento, descrição e timestamp.
        log_file.write(f"{evento},{descricao},{int(time.time())}\n")

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
		"endpoints": ["/", "/estatisticas"],
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
    return jsonify({
        "mensagem": "post funcional" # apenas teste
    })

 # Rota "/logs" → lê e retorna o conteúdo do arquivo de logs
@app.route('/logs')
def buscar_logs():
     # Caminho até o log.csv
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'log.csv')
    logs = []
     # Abre o log e lê cada linha como dicionário
    with open(log_path, 'r', encoding='utf-8') as log_file:
        leitor = csv.DictReader(log_file)
        logs = [
            {
                "evento": linha["evento"],
                "descricao": linha["descricao"],
                 # Converte o timestamp (número) em data legível
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(linha["timestamp"])))
            }
            for linha in leitor  # list comprehension: cria uma lista a partir do arquivo
        ]
     # Retorna os logs em formato JSON
    return jsonify(logs)

# --------------------------- EXECUÇÃO PRINCIPAL ---------------------------
# Inicializa o banco na primeira execução do script
init_db()
 
 # Só executa o servidor se o arquivo for executado diretamente (não importado)
if __name__ == '__main__':
	# Roda o servidor Flask em modo debug, acessível em todas as interfaces (0.0.0.0)
  app.run(host='0.0.0.0', port=5001, debug=True)

