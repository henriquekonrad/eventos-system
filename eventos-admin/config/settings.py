# config/settings.py
"""
Configurações centralizadas do sistema.
Padrão: Singleton implícito via módulo Python
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========== DATABASE ==========
DB_PATH = "data/attendant.db"

# ========== API ENDPOINTS ==========
class APIConfig:
    BASE_URL = "http://177.44.248.122"
    
    AUTH = f"{BASE_URL}:8001"
    EVENTOS = f"{BASE_URL}:8002"
    USUARIOS = f"{BASE_URL}:8003"
    INSCRICOES = f"{BASE_URL}:8004"
    INGRESSOS = f"{BASE_URL}:8005"
    CHECKINS = f"{BASE_URL}:8006"
    CERTIFICADOS = f"{BASE_URL}:8007"
    
    TIMEOUT = 6

# ========== API KEYS ==========
class APIKeys:
    AUTH = os.getenv("AUTH_API_KEY")
    EVENTOS = os.getenv("EVENTOS_API_KEY")
    USUARIOS = os.getenv("USUARIOS_API_KEY")
    INSCRICOES = os.getenv("INSCRICOES_API_KEY")
    INGRESSOS = os.getenv("INGRESSOS_API_KEY")
    CHECKINS = os.getenv("CHECKINS_API_KEY")
    CERTIFICADOS = os.getenv("CERTIFICADOS_API_KEY")

# ========== UI CONFIG ==========
class UIConfig:
    APPEARANCE_MODE = "System"
    COLOR_THEME = "blue"
    
    # Cores semânticas
    COLOR_SUCCESS = "green"
    COLOR_WARNING = "orange"
    COLOR_ERROR = "red"
    COLOR_INFO = "blue"
    
    # Tamanhos
    MAIN_WINDOW_SIZE = "1100x650"
    DIALOG_SMALL = "450x300"
    DIALOG_MEDIUM = "500x380"
    DIALOG_LARGE = "900x550"