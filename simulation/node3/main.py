import os
import sys
import json
import threading
import time
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import requests

# === CONFIGURAÇÃO DO NÓ ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_ID = os.path.basename(BASE_DIR)
PORT = 8003
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
QA_FILE = os.path.join(BASE_DIR, "qa.json")
PENDING_FILE = os.path.join(BASE_DIR, "pending_knowledge.json")

OTHER_NODES = [
    {"name": "node2", "url": "http://127.0.0.1:8002"},
    {"name": "node1", "url": "http://127.0.0.1:8001"},
]

# === INFRA BÁSICA ===
os.makedirs(WEIGHTS_DIR, exist_ok=True)

for path, default in [
    (LOG_FILE, "== LOG DO NÓ INICIADO ==\n"),
    (CONFIG_FILE, {"node_id": NODE_ID, "ip": "127.0.0.1", "port": PORT, "active": True}),
    (QA_FILE, {}),
    (PENDING_FILE, {}),
]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=4) if isinstance(default, dict) else f.write(default)

def log(msg):
    line = f"[{datetime.now().isoformat()}] {NODE_ID}: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def carregar_json(caminho):
    with open(caminho, "r") as f:
        return json.load(f)

def salvar_json(caminho, conteudo):
    with open(caminho, "w") as f:
        json.dump(conteudo, f, indent=4)

local_qa = carregar_json(QA_FILE)
pending_knowledge = carregar_json(PENDING_FILE)

# === FASTAPI SERVER ===
app = FastAPI()

@app.get("/ping")
def ping():
    return {"node": NODE_ID, "status": "alive"}

@app.post("/ask")
def ask(data: dict):
    question = data.get("question", "").lower().strip()
    answer = local_qa.get(question)
    return {"from": NODE_ID, "answer": answer or "não sei"}

@app.post("/receive_knowledge")
def receive_knowledge(data: dict):
    question = data.get("question", "").lower().strip()
    answer = data.get("answer", "").strip()

    if question in local_qa:
        return {"status": "já sei"}

    pending_knowledge.setdefault(question, {})
    pending_knowledge[question][answer] = pending_knowledge[question].get(answer, 0) + 1
    salvar_json(PENDING_FILE, pending_knowledge)

    if pending_knowledge[question][answer] >= 2:
        local_qa[question] = answer
        salvar_json(QA_FILE, local_qa)
        log(f"[CONSENSO] Aceitou '{question}' → '{answer}'")
        pending_knowledge.pop(question)
        salvar_json(PENDING_FILE, pending_knowledge)

    return {"status": "recebido"}

@app.get("/pending")
def pending():
    return pending_knowledge

# === BUSCA EXTERNA ===
def buscar_na_internet(pergunta):
    try:
        # Extrai termo da pergunta (pode ser melhorado depois com NLP)
        termo = pergunta.lower().replace("o que é", "").replace("quem foi", "").strip()
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo}"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "extract" in data and data["extract"]:
            return data["extract"]
        else:
            return None
    except Exception as e:
        log(f"Erro ao buscar na Wikipedia: {e}")
        return None


# === APRENDIZADO LOCAL + COMPARTILHAMENTO ===
def compartilhar_com_outros(question, answer):
    for node in OTHER_NODES:
        try:
            url = node["url"] + "/receive_knowledge"
            res = requests.post(url, json={"question": question, "answer": answer}, timeout=3)
            log(f"Enviei conhecimento a {node['name']}: {question} → {answer} ({res.status_code})")
        except Exception as e:
            log(f"Erro ao compartilhar com {node['name']}: {e}")

def perguntar_ao_sistema(pergunta):
    pergunta = pergunta.lower().strip()

    if pergunta in local_qa:
        resposta = local_qa[pergunta]
        log(f"Resposta local para '{pergunta}': {resposta}")
        return resposta

    log(f"Não sei responder '{pergunta}' — perguntando aos outros nós...")
    for node in OTHER_NODES:
        try:
            url = node["url"] + "/ask"
            res = requests.post(url, json={"question": pergunta}, timeout=3)
            resposta = res.json().get("answer")
            if resposta and resposta != "não sei":
                log(f"{node['name']} respondeu: '{resposta}' — aprendendo e compartilhando...")
                local_qa[pergunta] = resposta
                salvar_json(QA_FILE, local_qa)
                compartilhar_com_outros(pergunta, resposta)
                return resposta
        except Exception as e:
            log(f"Erro ao perguntar a {node['name']}: {e}")

    log(f"Nenhum nó respondeu — buscando na internet...")
    resposta = buscar_na_internet(pergunta)
    if resposta:
        log(f"Web respondeu: '{resposta}' — aprendendo e compartilhando...")
        local_qa[pergunta] = resposta
        salvar_json(QA_FILE, local_qa)
        compartilhar_com_outros(pergunta, resposta)
        return resposta

    log("Busca na internet falhou. Nenhuma resposta encontrada.")
    return "não sei"

# === INTERAÇÃO COM sys.stdin.readline() ===
def rotina_de_teste_interativo():
    while True:
        print(f"\n[{NODE_ID}] Pergunte algo: ", end="", flush=True)
        pergunta = sys.stdin.readline().strip()
        if pergunta.lower() in ("sair", "exit", "quit"):
            break
        resposta = perguntar_ao_sistema(pergunta)
        print(f"[{NODE_ID}] → {resposta}")

# === START ===
if __name__ == "__main__":
    log("Nó iniciado com chatbot + aprendizado + consenso + terminal corrigido.")
    threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error"), daemon=True).start()
    time.sleep(1)
    rotina_de_teste_interativo()
