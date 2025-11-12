# sync_manager.py
import sqlite3
import json
import os
import requests
from db import DB_PATH, add_inscrito_local, limpar_inscritos_evento, delete_pending_request, list_pending_requests
from api_client import is_online, auth_header

def sync_eventos():
    """
    Sincroniza eventos da API para o SQLite local.
    """
    if not is_online():
        print("[SYNC] Offline: não é possível sincronizar eventos")
        return
    
    headers = auth_header()
    headers["x-api-key"] = os.getenv("EVENTOS_API_KEY")
    
    try:
        url = "http://177.44.248.122:8002/eventos/publicos/ativos"
        r = requests.get(url, headers=headers, timeout=6)
        r.raise_for_status()
        eventos = r.json()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for ev in eventos:
            c.execute("""
                INSERT OR REPLACE INTO eventos (id, nome, data_inicio, atualizado_em)
                VALUES (?, ?, ?, ?)
            """, (
                ev["id"],
                ev.get("titulo", ""),
                ev.get("inicio_em", ""),
                ev.get("fim_em", "")
            ))
        conn.commit()
        conn.close()
        print(f"[SYNC] Sincronizados {len(eventos)} eventos")
    except Exception as e:
        print(f"[SYNC] Erro ao sincronizar eventos: {e}")


def sync_inscritos_evento(evento_id):
    """
    Baixa todos os inscritos de um evento específico.
    IMPORTANTE: Você precisa ter um endpoint na API que retorne os inscritos.
    Se não tiver, precisaremos adaptar.
    """
    if not is_online():
        print("[SYNC] Offline: não é possível sincronizar inscritos")
        return False
    
    headers = auth_header()
    headers["x-api-key"] = os.getenv("INSCRICOES_API_KEY")
    
    try:
        # ATENÇÃO: Este endpoint pode não existir na sua API!
        # Você vai precisar criar ou adaptar para usar outro endpoint
        url = f"http://177.44.248.122:8004/evento/{evento_id}/inscritos"
        
        print(f"[SYNC] Tentando baixar inscritos: {url}")
        r = requests.get(url, headers=headers, timeout=6)
        r.raise_for_status()
        inscritos = r.json()
        
        # Limpa inscritos antigos deste evento (apenas os já sincronizados)
        limpar_inscritos_evento(evento_id)
        
        # Salva novos inscritos
        for insc in inscritos:
            add_inscrito_local(
                inscricao_id=insc.get("id") or insc.get("inscricao_id"),
                evento_id=evento_id,
                nome=insc.get("nome", ""),
                cpf=insc.get("cpf", ""),
                email=insc.get("email", ""),
                sincronizado=1  # veio do servidor
            )
        
        print(f"[SYNC] ✓ Sincronizados {len(inscritos)} inscritos do evento")
        return True
        
    except requests.HTTPError as e:
        print(f"[SYNC] ✗ Erro HTTP ao sincronizar inscritos: {e.response.status_code}")
        print(f"[SYNC] Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"[SYNC] ✗ Erro ao sincronizar inscritos: {e}")
        return False


def process_pending():
    """
    Processa requisições pendentes quando voltar online.
    """
    if not is_online():
        print("[SYNC] Ainda offline, não é possível processar pendentes")
        return
    
    pendentes = list_pending_requests()
    if not pendentes:
        print("[SYNC] Nenhuma requisição pendente")
        return
    
    print(f"[SYNC] Processando {len(pendentes)} requisições pendentes...")
    
    sucesso = 0
    falhas = 0
    
    for p in pendentes:
        try:
            # Parse headers e body
            headers = json.loads(p.get("headers", "{}")) if p.get("headers") else {}
            
            # Adiciona API key apropriada baseada na URL
            if "8004" in p["url"]:  # inscricoes
                headers["x-api-key"] = os.getenv("INSCRICOES_API_KEY")
            elif "8006" in p["url"]:  # checkins
                headers["x-api-key"] = os.getenv("CHECKINS_API_KEY")
            
            body = json.loads(p["body"]) if p["body"] else None
            
            print(f"[SYNC] Processando: {p['method']} {p['url']}")
            print(f"[SYNC] Body: {body}")
            
            r = requests.request(
                p["method"],
                p["url"],
                json=body,
                headers=headers,
                timeout=6
            )
            
            print(f"[SYNC] Status: {r.status_code}")
            print(f"[SYNC] Response: {r.text}")
            
            r.raise_for_status()
            
            # Remove da fila se sucesso
            delete_pending_request(p["id"])
            sucesso += 1
            print(f"[SYNC] ✓ Sincronizado: {p['method']} {p['url']}")
            
        except requests.HTTPError as e:
            falhas += 1
            print(f"[SYNC] ✗ HTTP Error {e.response.status_code} ao sincronizar {p['id']}")
            print(f"[SYNC] Response: {e.response.text}")
            # Não remove da fila, tentará novamente depois
            
        except Exception as e:
            falhas += 1
            print(f"[SYNC] ✗ Falha ao sincronizar {p['id']}: {e}")
    
    print(f"[SYNC] Resultado: {sucesso} sucesso, {falhas} falhas")