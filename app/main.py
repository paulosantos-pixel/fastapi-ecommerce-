from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.dependencies import get_db
from app import crud, schemas, auth
from app.models import Categoria, Producto
from app.routers import productos

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "ok", "app": settings.PROJECT_NAME}

# ==================== AUTENTICACION ====================
@app.post("/registro", response_model=schemas.UsuarioResponse)
def registro(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = crud.obtener_usuario_por_email(db, usuario.email)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya esta registrado")
    return crud.crear_usuario(db, usuario)

@app.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = crud.obtener_usuario_por_email(db, usuario.email)
    if not db_usuario or db_usuario.contrasenia != usuario.contrasenia:
        raise HTTPException(status_code=400, detail="Email o contrasena incorrectos")
    token = auth.crear_token_acceso(db_usuario.id, db_usuario.email, db_usuario.es_admin)
    return {"token_acceso": token, "tipo_token": "bearer"}

# ==================== CATEGORIAS ====================
@app.get("/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.obtener_categorias(db)

@app.post("/categorias", response_model=schemas.CategoriaResponse)
def agregar_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado.")
    return crud.crear_categoria(db, categoria)

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado.")
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).first()
    if productos_asociados:
        raise HTTPException(status_code=400, detail="No se puede eliminar la categoria porque tiene productos asociados")
    db.delete(categoria)
    db.commit()
    return {"mensaje": f"Categoria '{categoria.nombre}' eliminada correctamente"}

# ==================== CARRITO ====================
@app.get("/carrito", response_model=schemas.CarritoResponse)
def ver_carrito(db: Session = Depends(get_db), token_valido: dict = Depends(auth.verificar_token)):
    usuario_id = token_valido.get("usuario_id")
    carrito = crud.obtener_carrito(db, usuario_id)
    return carrito

@app.post("/carrito/items", response_model=schemas.CarritoItemResponse)
def agregar_al_carrito(
    item: schemas.CarritoItemCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    return crud.agregar_item_carrito(db, usuario_id, item)

@app.delete("/carrito/items/{item_id}")
def eliminar_del_carrito(
    item_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    item = crud.eliminar_item_carrito(db, usuario_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"mensaje": "Item eliminado del carrito"}

@app.delete("/carrito/vaciar")
def vaciar_carrito(
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    crud.vaciar_carrito(db, usuario_id)
    return {"mensaje": "Carrito vaciado correctamente"}

# ==================== ROUTERS ====================
app.include_router(productos.router)