from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from jose import JWTError
from app.dependencies import get_db, get_current_user
from app.core.security import hash_password, verificar_password, crear_token, decodificar_token
from app.core.config import settings
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioOut, Token, RefreshIn

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(datos: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="Ese email ya existe")
    
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hash_password(datos.password),
        acepto_tratamiento=True,
        fecha_consentimiento=datetime.now(timezone.utc),
        rol="customer",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.email == form.username).first()
    if not u or not verificar_password(form.password, u.hashed_password):
        raise HTTPException(status_code=401, detail="Datos incorrectos")
    
    return {
        "access_token": crear_token(u.email, u.rol, settings.ACCESS_MIN, "access"),
        "refresh_token": crear_token(u.email, u.rol, settings.REFRESH_MIN, "refresh"),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh(datos: RefreshIn, db: Session = Depends(get_db)):
    try:
        p = decodificar_token(datos.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh inválido")
    
    if p.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Ese no es un refresh")
    
    u = db.query(Usuario).filter(Usuario.email == p.get("sub")).first()
    if not u:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return {
        "access_token": crear_token(u.email, u.rol, settings.ACCESS_MIN, "access"),
        "refresh_token": crear_token(u.email, u.rol, settings.REFRESH_MIN, "refresh"),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario