# services/api_service.py
"""
Service de comunicação com API.
Centraliza todas as chamadas HTTP.
Padrão Singleton: Mantém token único.
"""
import requests
from typing import Optional, Dict
from config.settings import APIConfig, APIKeys

class APIService:
    """
    Gerencia comunicação com API externa.
    Padrão Singleton implícito via atributo de classe.
    """
    
    _token: Optional[str] = None
    
    def __init__(self):
        self.timeout = APIConfig.TIMEOUT
    
    @classmethod
    def set_token(cls, token: str):
        """Define token de autenticação (após login)"""
        cls._token = token
        print("[API] Token definido")
    
    @classmethod
    def get_token(cls) -> Optional[str]:
        """Retorna token atual"""
        return cls._token
    
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
    
    # ========== AUTH ==========
    
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
    
    # ========== EVENTOS ==========
    
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
    
    # ========== INSCRIÇÕES ==========
    
    def listar_inscritos_evento(self, evento_id: str) -> Optional[list]:
        """Lista inscritos de um evento"""
        url = f"{APIConfig.INSCRICOES}/evento/{evento_id}/inscritos"
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
    
    # ========== INGRESSOS ==========
    
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
    
    # ========== USUÁRIOS ==========
    
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