# api_client.py
import requests
import json
import os
from dotenv import load_dotenv
from db import add_pending

load_dotenv()

BASE_AUTH = "http://177.44.248.122:8001"
BASE_EVENTOS = "http://177.44.248.122:8002"
BASE_USUARIOS = "http://177.44.248.122:8003"
BASE_INSCRICOES = "http://177.44.248.122:8004"
BASE_INGRESSOS = "http://177.44.248.122:8005"
BASE_CHECKINS = "http://177.44.248.122:8006"
BASE_CERT = "http://177.44.248.122:8007"

TIMEOUT = 6
TOKEN = None

def _request(method, url, json_body=None, params=None):
    headers = auth_header()
    headers["x-api-key"] = os.getenv("EVENTOS_API_KEY")
    try:
        print(f"[REQUEST] {method} {url}")
        if json_body:
            print(f"[REQUEST] Body: {json_body}")
        if params:
            print(f"[REQUEST] Params: {params}")
        r = requests.request(method, url, json=json_body, params=params, headers=headers, timeout=6)
        print(f"[REQUEST] Status: {r.status_code}")
        print(f"[REQUEST] Response: {r.text}")
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[REQUEST] Offline ou erro: {e}")
        from db import add_pending
        add_pending(method, url, json.dumps(json_body) if json_body else "", headers=json.dumps(headers))
        return None


def login(email, senha):
    """Login na API de auth, retorna access_token"""
    global TOKEN
    url = f"{BASE_AUTH}/login"
    headers = {
        "x-api-key": os.getenv("AUTH_API_KEY")
    }
    body = {"email": email, "senha": senha}
    try:
        r = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        TOKEN = data.get("access_token")
        print("Login efetuado com sucesso!")
        return TOKEN
    except requests.HTTPError as e:
        print("Erro no login:", e.response.text)
        return None

def auth_header():
    """Headers para requisições autenticadas"""
    if not TOKEN:
        raise Exception("Usuário não autenticado. Faça login primeiro.")
    return {
        "Authorization": f"Bearer {TOKEN}"
    }

def is_online():
    url = f"http://177.44.248.122:8002/eventos/publicos/ativos"
    headers = auth_header()
    headers["x-api-key"] = os.getenv("EVENTOS_API_KEY")
    try:
        r = requests.get(url, headers=headers, timeout=6)
        print(f"[is_online] GET {url} -> {r.status_code}")
        print(f"[is_online] Response: {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"[is_online] Erro ao testar conexão: {e}")
        return False


def _request(method, url, json_body=None, params=None):
    headers = auth_header()
    try:
        r = requests.request(method, url, json=json_body, params=params, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        # Se offline, salva na tabela pending
        body_text = json.dumps(json_body) if json_body else ""
        add_pending(method, url, body_text, headers=json.dumps(headers))
        print(f"Offline: requisição salva -> {url}")
        return None

# -----------------------------
# Funções da API usando _request
# -----------------------------
def listar_eventos_publicos():
    url = f"{BASE_EVENTOS}/eventos/publicos/ativos"
    return _request("GET", url)

def buscar_evento(evento_id):
    url = f"{BASE_EVENTOS}/{evento_id}"
    return _request("GET", url)

def inscricao_rapida(evento_id, nome, cpf, email):
    url = f"{BASE_INSCRICOES}/rapida"
    body = {"evento_id": evento_id, "nome_rapido": nome, "cpf_rapido": cpf, "email_rapido": email}
    return _request("POST", url, json_body=body)

def registrar_checkin(inscricao_id, ingresso_id, usuario_id):
    url = f"{BASE_CHECKINS}/"
    params = {"inscricao_id": inscricao_id, "ingresso_id": ingresso_id, "usuario_id": usuario_id}
    return _request("POST", url, params=params)

def emitir_certificado(inscricao_id, evento_id):
    url = f"{BASE_CERT}/emitir"
    body = {"inscricao_id": inscricao_id, "evento_id": evento_id}
    return _request("POST", url, json_body=body)
