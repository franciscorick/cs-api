import sqlite3
import os
import csv
from api.logger import log_event


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
