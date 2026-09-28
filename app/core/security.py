from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(p: str) -> str:
    """Hashea una contrasena con bcrypt."""
    return pwd.hash(p)


def verificar_password(plano: str, hashed: str) -> bool:
    """Verifica si una contrasena coincide con su hash."""
    return pwd.verify(plano, hashed)


def crear_token(email: str, rol: str, minutos: int, tipo: str) -> str:
    """Crea un token JWT con sub, rol, tipo y exp."""
    payload = {
        "sub": email,
        "rol": rol,
        "tipo": tipo,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutos),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decodifica y valida un token JWT."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])