# repositories/pending_repository.py
"""
Repository para Requisições Pendentes.
Gerencia fila de sincronização com API.
"""
from typing import List, Dict, Optional
from datetime import datetime
import json
from repositories.base_repository import BaseRepository

class PendingRepository(BaseRepository):
    
    def __init__(self):
        super().__init__("pending_requests")
    
    def create(self, method: str, url: str, body: dict, headers: dict,
               related_inscricao_id: Optional[str] = None,
               related_cpf: Optional[str] = None) -> int:
        """Adiciona requisição pendente na fila"""
        query = """
            INSERT INTO pending_requests 
            (method, url, body, headers, created_at, related_inscricao_id, related_cpf)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Serializa body e headers para JSON
        body_str = json.dumps(body) if isinstance(body, dict) else (body or "")
        headers_str = json.dumps(headers) if isinstance(headers, dict) else (headers or "{}")
        
        cursor = self._execute(
            query,
            (method, url, body_str, headers_str, datetime.utcnow().isoformat(),
             related_inscricao_id, related_cpf)
        )
        
        print(f"[REPO] Pendente adicionado: {method} {url} "
              f"(inscricao_id: {related_inscricao_id}, cpf: {related_cpf})")
        
        return cursor.lastrowid
    
    def find_all(self) -> List[Dict]:
        """Lista todas as requisições pendentes"""
        query = """
            SELECT id, method, url, body, headers, created_at, 
                   related_inscricao_id, related_cpf 
            FROM pending_requests 
            ORDER BY id ASC
        """
        rows = self._fetch_all(query)
        return [self._row_to_dict(row) for row in rows]
    
    def find_by_id(self, request_id: int) -> Optional[Dict]:
        """Busca requisição pendente por ID"""
        query = """
            SELECT id, method, url, body, headers, created_at, 
                   related_inscricao_id, related_cpf 
            FROM pending_requests 
            WHERE id = ?
        """
        row = self._fetch_one(query, (request_id,))
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def delete(self, request_id: int) -> Optional[Dict]:
        """
        Remove requisição pendente.
        Retorna informações sobre a requisição removida (para limpeza).
        """
        # Busca info antes de deletar
        info = self.find_by_id(request_id)
        
        # Deleta
        query = "DELETE FROM pending_requests WHERE id = ?"
        self._execute(query, (request_id,))
        
        print(f"[REPO] Pendente {request_id} removido")
        
        return info
    
    def count(self) -> int:
        """Conta requisições pendentes"""
        query = "SELECT COUNT(*) FROM pending_requests"
        row = self._fetch_one(query)
        return row[0] if row else 0
    
    def delete_all(self) -> int:
        """Remove todas as requisições pendentes (usar com cuidado!)"""
        query = "DELETE FROM pending_requests"
        cursor = self._execute(query)
        return cursor.rowcount
    
    def _row_to_dict(self, row: tuple) -> Dict:
        """Converte tupla do banco para dicionário"""
        return {
            "id": row[0],
            "method": row[1],
            "url": row[2],
            "body": row[3],
            "headers": row[4],
            "created_at": row[5],
            "related_inscricao_id": row[6],
            "related_cpf": row[7]
        }