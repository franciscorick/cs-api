import os
import time


def get_log_path():
    """Retorna o caminho do arquivo de log baseado no ambiente."""
    if os.environ.get('VERCEL_ENV'):
        return os.path.join('/tmp', 'log.csv')
    else:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'log.csv')


def log_event(evento, descricao):
    """Registra um evento no arquivo de log."""
    log_caminho = get_log_path()
    # Cria o diretório pai se não existir
    os.makedirs(os.path.dirname(log_caminho), exist_ok=True)

    # Verifica se o arquivo existe e se está vazio
    if not os.path.exists(log_caminho) or os.path.getsize(log_caminho) == 0:
        # Cria o arquivo e escreve o cabeçalho
        with open(log_caminho, 'w', encoding='utf-8') as log_file:
            log_file.write("evento,descricao,timestamp\n")

    # Adiciona o evento ao log
    with open(log_caminho, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{evento},{descricao},{int(time.time())}\n")
