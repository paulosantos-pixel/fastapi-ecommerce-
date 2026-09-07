import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"

security = HTTPBearer()

def crear_token_acceso(usuario_id: int, email: str, es_admin: bool):
    tiempo_expiracion = datetime.now(timezone.utc) + timedelta(minutes=60)
    datos_a_guardar = {
        "sub": email,
        "usuario_id": usuario_id,
        "email": email,
        "es_admin": es_admin,
        "exp": tiempo_expiracion
    }
    token_encriptado = jwt.encode(datos_a_guardar, SECRET_KEY, algorithm=ALGORITHM)
    return token_encriptado

def verificar_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return datos
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ya expiró")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido o falso")