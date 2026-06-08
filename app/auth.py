import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuraciones para firmar el token
SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"

security = HTTPBearer()

# Función para generar la pulserita (Token)
def crear_token_acceso(usuario: str):
    tiempo_expiracion = datetime.now(timezone.utc) + timedelta(minutes=30)
    datos_a_guardar = {"sub": usuario, "exp": tiempo_expiracion}
    token_encriptado = jwt.encode(datos_a_guardar, SECRET_KEY, algorithm=ALGORITHM)
    return token_encriptado

# Función para revisar si la pulserita es válida
def verificar_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return datos
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ya expiró")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido o falso")