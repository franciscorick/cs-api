#!/usr/bin/env python3
"""Script para executar a API localmente."""
from api.index import app

if __name__ == '__main__':
    # Executa a aplicação em modo debug
    app.run(host='0.0.0.0', port=5001, debug=True)
