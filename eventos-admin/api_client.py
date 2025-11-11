# api_client.py
import requests
import json
import os
from dotenv import load_dotenv
from db import add_pending

load_dotenv()

BASE_AUTH = "http://177.44.248.122:8001"
TOKEN = None

BASE_EVENTOS = "http://177.44.248.122:8002"
BASE_USUARIOS = "http://177.44.248.122:8003"
BASE_INSCRICOES = "http://177.44.248.122:8004"
BASE_INGRESSOS = "http://177.44.248.122:8005"
BASE_CHECKINS = "http://177.44.248.122:8006"
BASE_CERT = "http://177.44.248.122:8007"

TIMEOUT = 6

def login(email, senha):
    """
    Faz login na API de autenticação e salva o access_token global.
    """
    global TOKEN
    url = f"{BASE_AUTH}/login"
    headers = {
        "x-api-key": os.getenv("AUTH_API_KEY")
    }
    params = {
        "email": email,
        "senha": senha
    }
    body = {
        "email": email,
        "senha": senha
    }
    r = requests.post(url, headers=headers, params=params, json=body, timeout=6)
    r.raise_for_status()
    data = r.json()
    TOKEN = data.get("access_token")
    return TOKEN

def auth_header():
    if not TOKEN:
        raise Exception("Usuário não autenticado. Faça login primeiro.")
    return {"Authorization": f"Bearer {TOKEN}"}

def is_online():
    """Verifica se consegue se conectar à API de eventos"""
    try:
        r = requests.get(f"{BASE_EVENTOS}/publicos/ativos", headers=auth_header(), timeout=3)
        return r.status_code == 200
    except:
        return False

def _request(method, url, json_body=None, params=None):
    """Função auxiliar para requisições com suporte offline"""
    headers = auth_header()
    try:
        r = requests.request(method, url, json=json_body, params=params, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        # Se offline, salva na tabela de requisições pendentes
        body_text = json.dumps(json_body) if json_body else ""
        add_pending(method, url, body_text, headers=json.dumps(headers))
        print(f"Offline: requisição salva para envio posterior -> {url}")
        return None

# -----------------------------
# Funções da API usando _request
# -----------------------------

def listar_eventos_publicos():
    url = f"{BASE_EVENTOS}/publicos/ativos"
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
