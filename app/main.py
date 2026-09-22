from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import crud, schemas, auth
from app.database import get_db
from app.models import Categoria, Producto
from app.services import productos as productos_service

app = FastAPI(title="E-Commerce API", version="1.0.0")

# ==================== CONFIGURACIÓN DE CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTENTICACIÓN ====================

@app.post("/registro", response_model=schemas.UsuarioResponse)
def registro(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = crud.obtener_usuario_por_email(db, usuario.email)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.crear_usuario(db, usuario)


@app.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = crud.obtener_usuario_por_email(db, usuario.email)
    if not db_usuario or db_usuario.contrasenia != usuario.contrasenia:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    
    token = auth.crear_token_acceso(db_usuario.id, db_usuario.email, db_usuario.es_admin)
    return {"token_acceso": token, "tipo_token": "bearer"}


# ==================== PRODUCTOS ====================

@app.get("/productos", response_model=list[schemas.ProductoOut])
def listar_productos(
    skip: int = 0,
    limit: int = 10,
    nombre: str | None = None,
    precio_max: float | None = None,
    db: Session = Depends(get_db),
):
    return productos_service.listar_productos(db, skip, limit, nombre, precio_max)


@app.post("/productos", response_model=schemas.ProductoOut)
def agregar_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden crear productos.")
    return productos_service.crear_producto(db, producto)


@app.put("/productos/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden editar productos.")
    producto = crud.actualizar_producto(db, producto_id, datos)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.delete("/productos/{producto_id}")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden eliminar productos.")
    producto = crud.eliminar_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}


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
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden crear categorías.")
    return crud.crear_categoria(db, categoria)


@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden eliminar categorías.")
    
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).first()
    if productos_asociados:
        raise HTTPException(status_code=400, detail="No se puede eliminar la categoría porque tiene productos asociados")
    
    db.delete(categoria)
    db.commit()
    
    return {"mensaje": f"Categoría '{categoria.nombre}' eliminada correctamente"}


# ==================== CARRITO ====================

@app.get("/carrito", response_model=schemas.CarritoResponse)
def ver_carrito(
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
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