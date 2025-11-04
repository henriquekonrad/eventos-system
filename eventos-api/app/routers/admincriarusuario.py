from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password.strip())

def criar_admin():
    db = SessionLocal()
    senha_hash = hash_password("senha123")

    admin = Usuario(
        nome="Administrador",
        email="admin@empresa.com",
        senha_hash=senha_hash,
        papel="administrador",
        email_verificado=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("Usuário admin criado com ID:", admin.id)

if __name__ == "__main__":
    criar_admin()
