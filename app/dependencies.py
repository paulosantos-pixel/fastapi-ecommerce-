from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decodificar_token
from app.models import Usuario

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    error = HTTPException(status_code=401, detail="Credenciales inválidas")
    
    try:
        payload = decodificar_token(token)
        if payload.get("tipo") != "access":
            raise error
    except JWTError:
        raise error
    
    usuario = db.query(Usuario).filter(Usuario.email == payload.get("sub")).first()
    if usuario is None:
        raise error
    
    return usuario


def require_admin(usuario: Usuario = Depends(get_current_user)):
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Necesitás ser admin")
    return usuario