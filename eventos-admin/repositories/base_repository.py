# repositories/base_repository.py
"""
Padrão Repository: Abstrai o acesso ao banco de dados.
Facilita testes e mudança de banco no futuro.
"""
import sqlite3
from typing import List, Dict, Optional, Any
from config.settings import DB_PATH

class BaseRepository:
    """
    Classe base para repositórios.
    Implementa operações comuns de banco de dados.
    """
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db_path = DB_PATH
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa query e retorna cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return cursor
    
    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Executa query e retorna um resultado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
    
    def _fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        """Executa query e retorna todos os resultados"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def find_by_id(self, id_value: Any) -> Optional[Dict]:
        """Busca registro por ID (implementar nas subclasses)"""
        raise NotImplementedError
    
    def find_all(self) -> List[Dict]:
        """Retorna todos os registros (implementar nas subclasses)"""
        raise NotImplementedError
    
    def create(self, data: Dict) -> Any:
        """Cria novo registro (implementar nas subclasses)"""
        raise NotImplementedError
    
    def update(self, id_value: Any, data: Dict) -> bool:
        """Atualiza registro (implementar nas subclasses)"""
        raise NotImplementedError
    
    def delete(self, id_value: Any) -> bool:
        """Deleta registro (implementar nas subclasses)"""
        raise NotImplementedError