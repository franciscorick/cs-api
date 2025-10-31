from flask import Flask, jsonify, request
import csv
import time
import os
from api.database import get_db, init_db
from api.logger import get_log_path, log_event

app = Flask(__name__)

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
    log_path = get_log_path()
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

# Inicializa o DB na primeira execução
init_db()

if __name__ == '__main__':
	# Executa a aplicação em modo debug
  app.run(host='0.0.0.0', port=5001, debug=True)

