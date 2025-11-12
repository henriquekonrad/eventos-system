# db.py
import sqlite3
from datetime import datetime
import json

DB_PATH = "data/attendant.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id TEXT PRIMARY KEY,
        nome TEXT,
        data_inicio TEXT,
        atualizado_em TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS inscritos (
        inscricao_id TEXT PRIMARY KEY,
        evento_id TEXT,
        nome TEXT,
        cpf TEXT,
        email TEXT,
        sincronizado INTEGER DEFAULT 0,
        criado_em TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inscricao_id TEXT,
        ingresso_id TEXT,
        usuario_id TEXT,
        evento_id TEXT,
        tipo TEXT,
        sincronizado INTEGER DEFAULT 0,
        criado_em TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS pending_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT,
        url TEXT,
        body TEXT,
        headers TEXT,
        created_at TEXT,
        related_inscricao_id TEXT,
        related_cpf TEXT
    )""")
    
    # Migração: adiciona colunas se não existirem
    try:
        c.execute("ALTER TABLE pending_requests ADD COLUMN related_inscricao_id TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE pending_requests ADD COLUMN related_cpf TEXT")
    except:
        pass
    
    conn.commit()
    conn.close()

def add_pending(method, url, body, headers=None, related_inscricao_id=None, related_cpf=None):
    """
    Adiciona requisição pendente na fila
    body: dict ou string (será convertido para JSON string)
    headers: dict ou string (será convertido para JSON string)
    related_inscricao_id: ID da inscrição relacionada (para rastreamento)
    related_cpf: CPF relacionado (para rastreamento)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Garantir que body e headers são strings JSON
    body_str = json.dumps(body) if isinstance(body, dict) else (body or "")
    headers_str = json.dumps(headers) if isinstance(headers, dict) else (headers or "{}")
    
    c.execute(
        "INSERT INTO pending_requests (method,url,body,headers,created_at,related_inscricao_id,related_cpf) VALUES (?,?,?,?,?,?,?)",
        (method, url, body_str, headers_str, datetime.utcnow().isoformat(), related_inscricao_id, related_cpf)
    )
    conn.commit()
    conn.close()
    print(f"[DB] Adicionado pending: {method} {url} (inscricao_id: {related_inscricao_id}, cpf: {related_cpf})")

# ---------- helpers for events ----------
def upsert_evento(evento_id, nome, data_inicio):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
      INSERT INTO eventos (id,nome,data_inicio,atualizado_em)
      VALUES (?,?,?,?)
      ON CONFLICT(id) DO UPDATE SET nome=excluded.nome, data_inicio=excluded.data_inicio, atualizado_em=excluded.atualizado_em
    """, (evento_id, nome, data_inicio, now))
    conn.commit()
    conn.close()

def get_eventos_local():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,nome,data_inicio FROM eventos ORDER BY data_inicio")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "nome": r[1], "data_inicio": r[2]} for r in rows]

# ---------- helpers for inscritos ----------
def add_inscrito_local(inscricao_id, evento_id, nome, cpf, email, sincronizado=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created = datetime.utcnow().isoformat()
    c.execute("""
      INSERT OR REPLACE INTO inscritos (inscricao_id,evento_id,nome,cpf,email,sincronizado,criado_em)
      VALUES (?,?,?,?,?,?,?)
    """, (inscricao_id, evento_id, nome, cpf, email, sincronizado, created))
    conn.commit()
    conn.close()
    print(f"[DB] Inscrito salvo: {nome} (CPF: {cpf})")

def get_inscrito_by_cpf(cpf, evento_id=None):
    """
    Busca inscrito por CPF, opcionalmente filtrando por evento
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if evento_id:
        c.execute("SELECT inscricao_id,evento_id,nome,cpf,email,sincronizado FROM inscritos WHERE cpf=? AND evento_id=?", (cpf, evento_id))
    else:
        c.execute("SELECT inscricao_id,evento_id,nome,cpf,email,sincronizado FROM inscritos WHERE cpf=?", (cpf,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "inscricao_id": row[0],
        "evento_id": row[1],
        "nome": row[2],
        "cpf": row[3],
        "email": row[4],
        "sincronizado": row[5]
    }

def get_inscrito_by_id(inscricao_id):
    """
    Busca inscrito por ID da inscrição
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT inscricao_id,evento_id,nome,cpf,email,sincronizado FROM inscritos WHERE inscricao_id=?", (inscricao_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "inscricao_id": row[0],
        "evento_id": row[1],
        "nome": row[2],
        "cpf": row[3],
        "email": row[4],
        "sincronizado": row[5]
    }

def delete_inscrito_local(inscricao_id):
    """Remove um inscrito local (usado quando removemos pendência de inscrição rápida)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM inscritos WHERE inscricao_id=?", (inscricao_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Inscrito {inscricao_id} removido")

def list_inscritos_por_evento(evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT inscricao_id,nome,cpf,email,sincronizado FROM inscritos WHERE evento_id=?", (evento_id,))
    rows = c.fetchall()
    conn.close()
    return [{"inscricao_id":r[0],"nome":r[1],"cpf":r[2],"email":r[3],"sincronizado":r[4]} for r in rows]

def limpar_inscritos_evento(evento_id):
    """Remove inscritos locais de um evento antes de re-sincronizar"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM inscritos WHERE evento_id=? AND sincronizado=1", (evento_id,))
    conn.commit()
    conn.close()

# ---------- helpers for checkins ----------
def add_checkin_local(inscricao_id, ingresso_id, usuario_id, evento_id, tipo="normal", sincronizado=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created = datetime.utcnow().isoformat()
    c.execute("""
      INSERT INTO checkins (inscricao_id,ingresso_id,usuario_id,evento_id,tipo,sincronizado,criado_em)
      VALUES (?,?,?,?,?,?,?)
    """, (inscricao_id, ingresso_id, usuario_id, evento_id, tipo, sincronizado, created))
    conn.commit()
    conn.close()
    print(f"[DB] Check-in salvo: {inscricao_id} (tipo: {tipo})")

def delete_checkin_local(inscricao_id):
    """Remove check-in local de uma inscrição"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM checkins WHERE inscricao_id=?", (inscricao_id,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"[DB] Check-in removido: {inscricao_id} ({deleted} registro(s))")
    return deleted > 0

def checkin_ja_existe_local(inscricao_id):
    """
    Verifica se já existe check-in local (não sincronizado) para uma inscrição.
    Retorna dict com info ou None.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sincronizado FROM checkins WHERE inscricao_id=? LIMIT 1", (inscricao_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "existe": True,
        "sincronizado": row[0] == 1
    }

def checkin_ja_existe_por_cpf(cpf, evento_id):
    """
    Verifica se já existe check-in para um CPF em um evento específico.
    Retorna dict com info ou None.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Busca inscrição por CPF e evento
    c.execute("""
        SELECT i.inscricao_id 
        FROM inscritos i 
        WHERE i.cpf=? AND i.evento_id=?
    """, (cpf, evento_id))
    
    inscricao = c.fetchone()
    
    if not inscricao:
        conn.close()
        return None
    
    inscricao_id = inscricao[0]
    
    # Verifica se tem check-in
    c.execute("SELECT sincronizado FROM checkins WHERE inscricao_id=?", (inscricao_id,))
    checkin = c.fetchone()
    conn.close()
    
    if not checkin:
        return None
    
    return {
        "existe": True,
        "sincronizado": checkin[0] == 1,
        "inscricao_id": inscricao_id
    }

def marcar_checkin_sincronizado(inscricao_id):
    """Marca um check-in como sincronizado"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE checkins SET sincronizado=1 WHERE inscricao_id=?", (inscricao_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Check-in {inscricao_id} marcado como sincronizado")

def list_pending_requests():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,method,url,body,headers,created_at,related_inscricao_id,related_cpf FROM pending_requests ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"id":r[0],"method":r[1],"url":r[2],"body":r[3],"headers":r[4],"created_at":r[5],"related_inscricao_id":r[6],"related_cpf":r[7]} for r in rows]

def delete_pending_request(request_id):
    """
    Remove uma requisição pendente.
    Retorna informações sobre a requisição removida para limpeza de dados relacionados.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Busca informações antes de deletar
    c.execute("SELECT related_inscricao_id, related_cpf FROM pending_requests WHERE id=?", (request_id,))
    row = c.fetchone()
    
    # Deleta
    c.execute("DELETE FROM pending_requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()
    
    print(f"[DB] Pending {request_id} removido")
    
    if row:
        return {
            "inscricao_id": row[0],
            "cpf": row[1]
        }
    return None