import os
import json
from datetime import datetime

# Caminho base (garante que tudo seja salvo na pasta do próprio nó)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")

# Criar log.txt se não existir
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("== LOG DO NÓ INICIADO ==\n")

# Criar config.json se não existir
if not os.path.exists(CONFIG_FILE):
    default_config = {
        "node_id": os.path.basename(BASE_DIR),
        "ip": "127.0.0.1",
        "port": 8000,
        "active": True
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

# Criar pasta weights/ se não existir
if not os.path.exists(WEIGHTS_DIR):
    os.makedirs(WEIGHTS_DIR)

# Exemplo de log de inicialização
with open(LOG_FILE, "a") as f:
    f.write(f"[{datetime.now().isoformat()}] Nó {os.path.basename(BASE_DIR)} iniciado com sucesso.\n")

print(f"Nó {os.path.basename(BASE_DIR)} rodando com sucesso!")
