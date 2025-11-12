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
    """
    if not is_online():
        print("[SYNC] Offline: não é possível sincronizar inscritos")
        return False
    
    headers = auth_header()
    headers["x-api-key"] = os.getenv("INSCRICOES_API_KEY")
    
    try:
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
    VERSÃO ANTIGA - Mantida para compatibilidade
    Use process_pending_smart() para tratamento inteligente de erros
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
            
        except Exception as e:
            falhas += 1
            print(f"[SYNC] ✗ Falha ao sincronizar {p['id']}: {e}")
    
    print(f"[SYNC] Resultado: {sucesso} sucesso, {falhas} falhas")


def process_pending_smart():
    """
    Processa requisições pendentes com TRATAMENTO INTELIGENTE de erros.
    
    Erros que REMOVEM da fila (não faz sentido retentar):
    - 400: Check-in já realizado
    - 400: Usuário já inscrito
    - 404: Recurso não encontrado (pode ter sido deletado)
    - 409: Conflito de dados
    
    Erros que MANTÊM na fila (podem funcionar depois):
    - 500: Erro interno do servidor
    - 503: Serviço indisponível
    - Timeout: Problemas de rede
    
    Retorna:
        dict com contadores: {sucesso, falhas, ja_feito, removidos}
    """
    if not is_online():
        print("[SYNC] Ainda offline, não é possível processar pendentes")
        return {"sucesso": 0, "falhas": 0, "ja_feito": 0, "removidos": 0}
    
    pendentes = list_pending_requests()
    if not pendentes:
        print("[SYNC] Nenhuma requisição pendente")
        return {"sucesso": 0, "falhas": 0, "ja_feito": 0, "removidos": 0}
    
    print(f"[SYNC] Processando {len(pendentes)} requisições pendentes...")
    
    sucesso = 0
    falhas = 0
    ja_feito = 0  # Check-ins/inscrições já realizados
    removidos = 0  # Erros permanentes removidos
    
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
            
            r = requests.request(
                p["method"],
                p["url"],
                json=body,
                headers=headers,
                timeout=6
            )
            
            print(f"[SYNC] Status: {r.status_code}")
            print(f"[SYNC] Response: {r.text[:200]}")  # Primeiros 200 chars
            
            # SUCESSO
            if r.status_code in [200, 201, 204]:
                delete_pending_request(p["id"])
                sucesso += 1
                print(f"[SYNC] ✓ Sincronizado com sucesso!")
                continue
            
            # ERROS 4xx - Analisar se deve remover ou manter
            if r.status_code >= 400 and r.status_code < 500:
                response_text = r.text.lower()
                deve_remover = False
                
                # Check-in já realizado - OK, pessoa pode entrar!
                if "já foi realizado" in response_text or "já registrado" in response_text:
                    print(f"[SYNC] ℹ️ Check-in já foi realizado - REMOVENDO da fila")
                    delete_pending_request(p["id"])
                    ja_feito += 1
                    continue
                
                # Usuário já inscrito - OK!
                if "já inscrito" in response_text or "already exists" in response_text:
                    print(f"[SYNC] ℹ️ Inscrição já existe - REMOVENDO da fila")
                    delete_pending_request(p["id"])
                    ja_feito += 1
                    continue
                
                # Recurso não encontrado - Pode ter sido deletado
                if r.status_code == 404:
                    print(f"[SYNC] ⚠️ Recurso não encontrado (404) - REMOVENDO da fila")
                    delete_pending_request(p["id"])
                    removidos += 1
                    continue
                
                # Conflito de dados
                if r.status_code == 409:
                    print(f"[SYNC] ⚠️ Conflito de dados (409) - REMOVENDO da fila")
                    delete_pending_request(p["id"])
                    removidos += 1
                    continue
                
                # Bad Request genérico - Pode ser erro de dados
                if r.status_code == 400:
                    print(f"[SYNC] ⚠️ Requisição inválida (400) - REMOVENDO da fila")
                    print(f"[SYNC] Detalhe: {response_text[:200]}")
                    delete_pending_request(p["id"])
                    removidos += 1
                    continue
                
                # Outros erros 4xx - Mantém na fila (pode ser temporário)
                print(f"[SYNC] ✗ Erro {r.status_code} - MANTENDO na fila para retentar")
                falhas += 1
                continue
            
            # ERROS 5xx - Mantém na fila (erro do servidor)
            if r.status_code >= 500:
                print(f"[SYNC] ✗ Erro do servidor ({r.status_code}) - MANTENDO na fila")
                falhas += 1
                continue
            
            # Outros casos
            print(f"[SYNC] ⚠️ Status desconhecido {r.status_code} - MANTENDO na fila")
            falhas += 1
            
        except requests.Timeout:
            print(f"[SYNC] ⏱️ Timeout na requisição - MANTENDO na fila")
            falhas += 1
            
        except requests.ConnectionError:
            print(f"[SYNC] 🔌 Erro de conexão - MANTENDO na fila")
            falhas += 1
            
        except Exception as e:
            print(f"[SYNC] ✗ Erro inesperado: {e} - MANTENDO na fila")
            falhas += 1
    
    resultado = {
        "sucesso": sucesso,
        "falhas": falhas,
        "ja_feito": ja_feito,
        "removidos": removidos
    }
    
    print(f"[SYNC] Resultado: {sucesso} sucesso, {falhas} falhas temporárias, "
          f"{ja_feito} já realizados, {removidos} erros permanentes")
    
    return resultado