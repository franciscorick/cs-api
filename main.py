from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
	"""Rota principal que retorna um JSON simples"""
	return jsonify({
		"mensagem": "API Flask ativa",
		"status": "ok",
		"endpoints": ["/"],
		"versao": "1.0.0"
	})


if __name__ == '__main__':
	# Executa a aplicação em modo debug
	app.run(host='0.0.0.0', port=5001, debug=True)