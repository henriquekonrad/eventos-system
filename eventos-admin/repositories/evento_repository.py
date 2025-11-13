# repositories/evento_repository.py
"""
Repository para Eventos.
Gerencia operações de banco relacionadas a eventos.
"""
from typing import Optional, List, Dict
from datetime import datetime
from repositories.base_repository import BaseRepository

class EventoRepository(BaseRepository):
    
    def __init__(self):
        super().__init__("eventos")
    
    def create_or_update(self, evento_id: str, nome: str, data_inicio: str) -> str:
        """Cria ou atualiza um evento (upsert)"""
        query = """
            INSERT INTO eventos (id, nome, data_inicio, atualizado_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                nome = excluded.nome, 
                data_inicio = excluded.data_inicio, 
                atualizado_em = excluded.atualizado_em
        """
        now = datetime.utcnow().isoformat()
        self._execute(query, (evento_id, nome, data_inicio, now))
        return evento_id
    
    def find_by_id(self, evento_id: str) -> Optional[Dict]:
        """Busca evento por ID"""
        query = "SELECT id, nome, data_inicio, atualizado_em FROM eventos WHERE id = ?"
        row = self._fetch_one(query, (evento_id,))
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def find_all(self, order_by: str = "data_inicio") -> List[Dict]:
        """Lista todos os eventos"""
        query = f"SELECT id, nome, data_inicio, atualizado_em FROM eventos ORDER BY {order_by}"
        rows = self._fetch_all(query)
        return [self._row_to_dict(row) for row in rows]
    
    def delete(self, evento_id: str) -> bool:
        """Remove um evento"""
        query = "DELETE FROM eventos WHERE id = ?"
        cursor = self._execute(query, (evento_id,))
        return cursor.rowcount > 0
    
    def count(self) -> int:
        """Conta total de eventos"""
        query = "SELECT COUNT(*) FROM eventos"
        row = self._fetch_one(query)
        return row[0] if row else 0
    
    def _row_to_dict(self, row: tuple) -> Dict:
        """Converte tupla do banco para dicionário"""
        return {
            "id": row[0],
            "nome": row[1],
            "data_inicio": row[2],
            "atualizado_em": row[3]
        }