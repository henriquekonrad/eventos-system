# sync_manager.py
import sqlite3, json, time
from db import DB_PATH, upsert_evento, add_inscrito_local, add_pending, get_eventos_local
from api_client import is_online, listar_eventos_publicos, registrar_checkin, inscricao_rapida
import requests

def sync_eventos():
    """
    Sincroniza eventos da API para o SQLite local.
    """
    if not is_online():
        print("Offline: não é possível sincronizar eventos")
        return

    # headers com token + api key
    headers = auth_header()
    headers["x-api-key"] = os.getenv("EVENTOS_API_KEY")

    try:
        eventos = listar_eventos_publicos()  # já retorna JSON da API

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        for ev in eventos:
            c.execute("""
                INSERT OR REPLACE INTO eventos (id, nome, data_inicio, atualizado_em)
                VALUES (?, ?, ?, ?)
            """, (
                ev["id"],
                ev.get("nome", ""),
                ev.get("data_inicio", ""),
                ev.get("atualizado_em", "")
            ))

        conn.commit()
        conn.close()
        print("Sincronização de eventos concluída.")
    except Exception as e:
        print("Erro ao sincronizar eventos:", e)

def process_pending():
    """Envia todas as requisições pendentes para o servidor"""
    if not is_online():
        print("Offline: requisições pendentes não enviadas")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, method, url, body FROM pending_requests ORDER BY id ASC")
    rows = c.fetchall()

    for rid, method, url, body in rows:
        try:
            data = json.loads(body) if body else None
            if method.upper() == "POST":
                r = requests.post(url, json=data, timeout=6)
            elif method.upper() == "GET":
                r = requests.get(url, timeout=6)
            else:
                r = requests.request(method, url, json=data, timeout=6)
            
            if 200 <= r.status_code < 300:
                # se for inscrição rápida, tenta capturar o server_id
                if "rapida" in url.lower() and r.content:
                    resp_json = r.json()
                    server_id = resp_json.get("inscricao_id")
                    local_id = data.get("evento_id")  # assume que guardou local_id em evento_id temporário
                    if server_id and local_id:
                        # atualizar inscrição local para ter server_id
                        c.execute("UPDATE inscritos SET inscricao_id=?, sincronizado=1 WHERE inscricao_id=?",
                                  (server_id, local_id))
                else:
                    # marca como sincronizado, se necessário
                    pass
                c.execute("DELETE FROM pending_requests WHERE id=?", (rid,))
                conn.commit()
                print(f"Requisição pendente {rid} enviada com sucesso.")
            else:
                print(f"Falha ao enviar requisição {rid}: {r.status_code}")
        except Exception as e:
            print(f"Erro ao processar requisição {rid}: {e}")
    conn.close()

def full_sync():
    """Faz sync completo: eventos + pendentes"""
    sync_eventos()
    process_pending()
