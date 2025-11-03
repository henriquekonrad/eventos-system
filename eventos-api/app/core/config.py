import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave_super_secreta")
    ALGORITHM: str = "HS256"

settings = Settings()
