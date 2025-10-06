from flask import Flask, jsonify
import datetime

app = Flask(__name__)

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
		"mensagem": "API Flask ativa",
		"status": "ok",
		"endpoints": ["/"],
		"versao": "1.0.0"
	})

@app.route('/estatisticas')
def ola():
    estatistica = Estatisticas("Chico", 21, 12, 10, 2300, datetime.date(2025,10,1), 8000 )
    return jsonify({
          "nome": estatistica.nome,
          "abates": estatistica.abates,
          "mortes": estatistica.mortes,
          "assistencias": estatistica.assistencias,
          "dano": estatistica.dano,
          "data": estatistica.data,
          "dinheiro": estatistica.dinheiro
    })

@app.route('/estatisticas', methods=['POST'])
def posta_estatistica():
     return jsonify({
          "mensagem": "post funcional"
     })


if __name__ == '__main__':
	# Executa a aplicação em modo debug
	app.run(host='0.0.0.0', port=5001, debug=True)