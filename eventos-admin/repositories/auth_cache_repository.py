from typing import Optional, Dict
from datetime import datetime
from repositories.base_repository import BaseRepository

class AuthCacheRepository(BaseRepository):
    def __init__(self):
        super().__init__("auth_cache")
    
    def save_token(self, token: str, email: str) -> bool:
        """
        Salva token no cache.
        """
        query = """
            INSERT OR REPLACE INTO auth_cache (id, token, email, saved_at)
            VALUES (1, ?, ?, ?)
        """
        self._execute(query, (token, email, datetime.utcnow().isoformat()))
        print(f"[REPO] Token salvo no cache para {email}")
        return True
    
    def get_token(self) -> Optional[Dict]:
        """
        Recupera token do cache.
        """
        query = "SELECT token, email, saved_at FROM auth_cache WHERE id = 1"
        row = self._fetch_one(query)
        
        if not row:
            return None
        
        return {
            "token": row[0],
            "email": row[1],
            "saved_at": row[2]
        }
    
    def clear_token(self) -> bool:
        """Remove token do cache (logout)"""
        query = "DELETE FROM auth_cache WHERE id = 1"
        self._execute(query)
        print("[REPO] Token removido do cache")
        return True
    
    def has_valid_token(self) -> bool:
        """
        Verifica se existe token válido no cache.
        """
        token_data = self.get_token()
        return token_data is not None and token_data['token'] is not None