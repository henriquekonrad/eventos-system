import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_PATH = "data/attendant.db"

# Endpoints
class APIConfig:
    BASE_URL = os.getenv("BASE_URL")
    
    AUTH = f"{BASE_URL}:8001"
    EVENTOS = f"{BASE_URL}:8002"
    USUARIOS = f"{BASE_URL}:8003"
    INSCRICOES = f"{BASE_URL}:8004"
    INGRESSOS = f"{BASE_URL}:8005"
    CHECKINS = f"{BASE_URL}:8006"
    CERTIFICADOS = f"{BASE_URL}:8007"
    
    TIMEOUT = 6

# Keys
class APIKeys:
    AUTH = os.getenv("AUTH_API_KEY")
    EVENTOS = os.getenv("EVENTOS_API_KEY")
    USUARIOS = os.getenv("USUARIOS_API_KEY")
    INSCRICOES = os.getenv("INSCRICOES_API_KEY")
    INGRESSOS = os.getenv("INGRESSOS_API_KEY")
    CHECKINS = os.getenv("CHECKINS_API_KEY")
    CERTIFICADOS = os.getenv("CERTIFICADOS_API_KEY")

# Config geral UI
class UIConfig:
    APPEARANCE_MODE = "dark"
    COLOR_THEME = "blue"
    
    COLOR_SUCCESS = "green"
    COLOR_WARNING = "orange"
    COLOR_ERROR = "red"
    COLOR_INFO = "blue"
    COLOR_RAPIDA = "#e08f3f"
    
    MAIN_WINDOW_SIZE = "1100x650"
    DIALOG_SMALL = "450x300"
    DIALOG_MEDIUM = "500x380"
    DIALOG_LARGE = "900x550"