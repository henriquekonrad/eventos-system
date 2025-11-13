# repositories/inscrito_repository.py
"""
Repository para Inscritos.
Gerencia operações de banco relacionadas a inscrições.
"""
from typing import Optional, List, Dict
from datetime import datetime
from repositories.base_repository import BaseRepository

class InscritoRepository(BaseRepository):
    
    def __init__(self):
        super().__init__("inscritos")
    
    def create(self, inscricao_id: str, evento_id: str, nome: str, 
               cpf: str, email: str, sincronizado: int = 0) -> str:
        """Cria novo inscrito"""
        query = """
            INSERT OR REPLACE INTO inscritos 
            (inscricao_id, evento_id, nome, cpf, email, sincronizado, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self._execute(
            query,
            (inscricao_id, evento_id, nome, cpf, email, sincronizado, 
             datetime.utcnow().isoformat())
        )
        print(f"[REPO] Inscrito salvo: {nome} (CPF: {cpf})")
        return inscricao_id
    
    def find_by_id(self, inscricao_id: str) -> Optional[Dict]:
        """Busca inscrito por ID"""
        query = """
            SELECT inscricao_id, evento_id, nome, cpf, email, sincronizado 
            FROM inscritos 
            WHERE inscricao_id = ?
        """
        row = self._fetch_one(query, (inscricao_id,))
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def find_by_cpf(self, cpf: str, evento_id: Optional[str] = None) -> Optional[Dict]:
        """Busca inscrito por CPF, opcionalmente filtrando por evento"""
        if evento_id:
            query = """
                SELECT inscricao_id, evento_id, nome, cpf, email, sincronizado 
                FROM inscritos 
                WHERE cpf = ? AND evento_id = ?
            """
            row = self._fetch_one(query, (cpf, evento_id))
        else:
            query = """
                SELECT inscricao_id, evento_id, nome, cpf, email, sincronizado 
                FROM inscritos 
                WHERE cpf = ?
            """
            row = self._fetch_one(query, (cpf,))
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def find_by_evento(self, evento_id: str) -> List[Dict]:
        """Lista todos os inscritos de um evento"""
        query = """
            SELECT inscricao_id, evento_id, nome, cpf, email, sincronizado 
            FROM inscritos 
            WHERE evento_id = ?
        """
        rows = self._fetch_all(query, (evento_id,))
        return [self._row_to_dict(row) for row in rows]
    
    def delete(self, inscricao_id: str) -> bool:
        """Remove um inscrito"""
        query = "DELETE FROM inscritos WHERE inscricao_id = ?"
        cursor = self._execute(query, (inscricao_id,))
        print(f"[REPO] Inscrito {inscricao_id} removido")
        return cursor.rowcount > 0
    
    def delete_by_evento_synced(self, evento_id: str) -> int:
        """Remove inscritos sincronizados de um evento (para re-sync)"""
        query = "DELETE FROM inscritos WHERE evento_id = ? AND sincronizado = 1"
        cursor = self._execute(query, (evento_id,))
        return cursor.rowcount
    
    def count_by_evento(self, evento_id: str) -> int:
        """Conta inscritos de um evento"""
        query = "SELECT COUNT(*) FROM inscritos WHERE evento_id = ?"
        row = self._fetch_one(query, (evento_id,))
        return row[0] if row else 0
    
    def _row_to_dict(self, row: tuple) -> Dict:
        """Converte tupla do banco para dicionário"""
        return {
            "inscricao_id": row[0],
            "evento_id": row[1],
            "nome": row[2],
            "cpf": row[3],
            "email": row[4],
            "sincronizado": row[5]
        }