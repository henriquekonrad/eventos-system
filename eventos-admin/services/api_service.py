import requests
from typing import Optional, Dict
from config.settings import APIConfig, APIKeys

class APIService:
    """
    Gerencia comunicação com API externa.
    """
    
    def __init__(self):
        self.timeout = APIConfig.TIMEOUT
        self._token = None
        self._token_loaded_from_cache = False
        self._load_token_from_cache()
        self.timeout = APIConfig.TIMEOUT
    
    def _load_token_from_cache(self):
        """Carrega token do cache SQLite (se existir)"""
        if self._token_loaded_from_cache:
            return
        
        try:
            from repositories.auth_cache_repository import AuthCacheRepository
            cache_repo = AuthCacheRepository()
            
            cached = cache_repo.get_token()
            if cached and cached['token']:
                self._token = cached['token']
                self._token_loaded_from_cache = True
            else:
                print("[API] Nenhum token em cache")
        except Exception as e:
            print(f"[API] Erro ao carregar token do cache: {e}")
    
    def set_token(cls, token: str, email: str = ""):
        """Define token de autenticação e salva no cache"""
        cls._token = token
        
        # Salva no cache
        try:
            from repositories.auth_cache_repository import AuthCacheRepository
            cache_repo = AuthCacheRepository()
            cache_repo.save_token(token, email)
            print(f"[API] Token definido e salvo no cache")
        except Exception as e:
            print(f"[API] Erro ao salvar token no cache: {e}")
    
    def clear_token(cls):
        """Remove token (logout)"""
        cls._token = None
        
        try:
            from repositories.auth_cache_repository import AuthCacheRepository
            cache_repo = AuthCacheRepository()
            cache_repo.clear_token()
            print("[API] Token limpo")
        except Exception as e:
            print(f"[API] Erro ao limpar token: {e}")
    
    def get_token(cls) -> Optional[str]:
        """Retorna token atual"""
        return cls._token
    
    def has_token(cls) -> bool:
        """Verifica se tem token disponível"""
        return cls._token is not None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers com autenticação"""
        if not self._token:
            raise Exception("Token não definido. Faça login primeiro.")
        
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
    
    def is_online(self) -> bool:
        """Testa conectividade com API"""
        try:
            headers = self.get_auth_headers()
            headers["x-api-key"] = APIKeys.EVENTOS
            
            url = f"{APIConfig.EVENTOS}/eventos/publicos/ativos"
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            print(f"[API] Teste de conexão: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[API] Erro ao testar conexão: {e}")
            return False
    
    # AUTH
    
    def login(self, email: str, senha: str) -> Optional[str]:
        """Faz login e retorna token"""
        url = f"{APIConfig.AUTH}/login"
        headers = {"x-api-key": APIKeys.AUTH}
        body = {"email": email, "senha": senha}
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=body, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            token = data.get("access_token")
            
            if token:
                self.set_token(token)
                print("[API] Login realizado com sucesso")
            
            return token
            
        except requests.HTTPError as e:
            print(f"[API] Erro no login: {e.response.text}")
            return None
        except Exception as e:
            print(f"[API] Erro: {e}")
            return None
    
    # EVENTOS
    
    def listar_eventos_publicos(self) -> Optional[list]:
        """Lista eventos públicos ativos"""
        url = f"{APIConfig.EVENTOS}/eventos/publicos/ativos"
        headers = self.get_auth_headers()
        headers["x-api-key"] = APIKeys.EVENTOS
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[API] Erro ao listar eventos: {e}")
            return None
    
    def buscar_evento(self, evento_id: str) -> Optional[Dict]:
        """Busca evento por ID"""
        url = f"{APIConfig.EVENTOS}/{evento_id}"
        headers = self.get_auth_headers()
        headers["x-api-key"] = APIKeys.EVENTOS
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[API] Erro ao buscar evento: {e}")
            return None
    
    # INSCRIÇÕES

    def listar_inscritos_evento(self, evento_id: str, incluir_canceladas: bool = True) -> Optional[list]:
        """
        Lista inscritos de um evento.
        
        Args:
            evento_id: ID do evento
            incluir_canceladas: Se True, inclui inscrições canceladas 
                            (necessário para o app saber quem cancelou)
        """
        url = f"{APIConfig.INSCRICOES}/evento/{evento_id}/inscritos"
        
        # Adiciona query param para incluir canceladas
        if incluir_canceladas:
            url += "?incluir_canceladas=true"
        
        headers = self.get_auth_headers()
        headers["x-api-key"] = APIKeys.INSCRICOES
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"[API] Erro HTTP {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            print(f"[API] Erro: {e}")
            return None
    
    # INGRESSOS
    
    def buscar_ingresso(self, inscricao_id: str) -> Optional[Dict]:
        """Busca ingresso por inscrição"""
        url = f"{APIConfig.INGRESSOS}/inscricao/{inscricao_id}/ingresso"
        headers = self.get_auth_headers()
        headers["x-api-key"] = APIKeys.INGRESSOS
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"[API] Erro ao buscar ingresso: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"[API] Erro: {e}")
            return None
    
    # USUARIOS
    
    def buscar_usuario_por_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        url = f"{APIConfig.USUARIOS}/email/{email}"
        headers = self.get_auth_headers()
        headers["x-api-key"] = APIKeys.USUARIOS
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"[API] Erro ao buscar usuário: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"[API] Erro: {e}")
            return None