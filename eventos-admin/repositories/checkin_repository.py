# repositories/checkin_repository.py
"""
Repository para Check-ins.
Encapsula todas as operações de banco relacionadas a check-ins.
"""
from typing import Optional, Dict
from datetime import datetime
from repositories.base_repository import BaseRepository

class CheckinRepository(BaseRepository):
    
    def __init__(self):
        super().__init__("checkins")
    
    def create(self, inscricao_id: str, ingresso_id: Optional[str], 
               usuario_id: Optional[str], evento_id: str, 
               tipo: str = "normal", sincronizado: int = 0) -> int:
        """Cria novo check-in"""
        query = """
            INSERT INTO checkins 
            (inscricao_id, ingresso_id, usuario_id, evento_id, tipo, sincronizado, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self._execute(
            query,
            (inscricao_id, ingresso_id, usuario_id, evento_id, tipo, 
             sincronizado, datetime.utcnow().isoformat())
        )
        return cursor.lastrowid
    
    def find_by_inscricao(self, inscricao_id: str) -> Optional[Dict]:
        """Busca check-in por ID de inscrição"""
        query = "SELECT * FROM checkins WHERE inscricao_id = ? LIMIT 1"
        row = self._fetch_one(query, (inscricao_id,))
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "inscricao_id": row[1],
            "ingresso_id": row[2],
            "usuario_id": row[3],
            "evento_id": row[4],
            "tipo": row[5],
            "sincronizado": row[6],
            "criado_em": row[7]
        }
    
    def exists_by_inscricao(self, inscricao_id: str) -> Optional[Dict]:
        """
        Verifica se check-in existe e retorna status.
        Retorna dict com {existe: bool, sincronizado: bool} ou None
        """
        query = "SELECT sincronizado FROM checkins WHERE inscricao_id = ? LIMIT 1"
        row = self._fetch_one(query, (inscricao_id,))
        
        if not row:
            return None
        
        return {
            "existe": True,
            "sincronizado": row[0] == 1
        }
    
    def delete_by_inscricao(self, inscricao_id: str) -> bool:
        """Remove check-in por inscrição"""
        query = "DELETE FROM checkins WHERE inscricao_id = ?"
        cursor = self._execute(query, (inscricao_id,))
        return cursor.rowcount > 0
    
    def mark_as_synced(self, inscricao_id: str) -> bool:
        """Marca check-in como sincronizado"""
        query = "UPDATE checkins SET sincronizado = 1 WHERE inscricao_id = ?"
        cursor = self._execute(query, (inscricao_id,))
        return cursor.rowcount > 0
    
    def count_by_evento(self, evento_id: str) -> int:
        """Conta check-ins de um evento"""
        query = "SELECT COUNT(*) FROM checkins WHERE evento_id = ?"
        row = self._fetch_one(query, (evento_id,))
        return row[0] if row else 0