from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # <-- AGREGAR ESTA LÍNEA
from sqlalchemy.orm import Session
from app import crud, schemas, auth
from app.database import get_db
from app.models import Categoria, Producto

app = FastAPI(title="E-Commerce API", version="1.0.0")

# ==================== CONFIGURACIÓN DE CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # El puerto donde corre el frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTENTICACIÓN ====================

@app.post("/registro", response_model=schemas.UsuarioResponse)
def registro(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    usuario_existente = crud.obtener_usuario_por_email(db, usuario.email)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.crear_usuario(db, usuario)

@app.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = crud.obtener_usuario_por_email(db, usuario.email)
    if not db_usuario or db_usuario.contrasenia != usuario.contrasenia:  # ¡HASHEAR EN PRODUCCIÓN!
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    
    token = auth.crear_token_acceso(db_usuario.id, db_usuario.email, db_usuario.es_admin)
    return {"token_acceso": token, "tipo_token": "bearer"}

# ==================== PRODUCTOS ====================

@app.get("/productos", response_model=list[schemas.ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return crud.obtener_productos(db)

# 🔒 Solo Admin - Crear producto
@app.post("/productos", response_model=schemas.ProductoResponse)
def agregar_producto(
    producto: schemas.ProductoCreate, 
    db: Session = Depends(get_db), 
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden crear productos.")
    return crud.crear_producto(db, producto)

# 🔒 Solo Admin - Actualizar producto
@app.put("/productos/{id}", response_model=schemas.ProductoResponse)
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

# 🔒 Solo Admin - Eliminar producto
@app.delete("/productos/{id}")
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

# 🔓 Público - Ver categorías (NO requiere token)
@app.get("/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.obtener_categorias(db)

# 🔒 Solo Admin - Crear categoría
@app.post("/categorias", response_model=schemas.CategoriaResponse)
def agregar_categoria(
    categoria: schemas.CategoriaCreate, 
    db: Session = Depends(get_db), 
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden crear categorías.")
    return crud.crear_categoria(db, categoria)

# 🔒 Solo Admin - Eliminar categoría
@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    # Verificar que sea admin
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden eliminar categorías.")
    
    # Buscar la categoría
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar que no tenga productos asociados
    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).first()
    if productos_asociados:
        raise HTTPException(status_code=400, detail="No se puede eliminar la categoría porque tiene productos asociados")
    
    # Eliminar la categoría
    db.delete(categoria)
    db.commit()
    
    return {"mensaje": f"Categoría '{categoria.nombre}' eliminada correctamente"}

# ==================== CARRITO ====================

# 🔒 Privado - Ver mi carrito
@app.get("/carrito", response_model=schemas.CarritoResponse)
def ver_carrito(
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    carrito = crud.obtener_carrito(db, usuario_id)
    return carrito

# 🔒 Privado - Agregar producto al carrito
@app.post("/carrito/items", response_model=schemas.CarritoItemResponse)
def agregar_al_carrito(
    item: schemas.CarritoItemCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    return crud.agregar_item_carrito(db, usuario_id, item)

# 🔒 Privado - Eliminar item del carrito
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

# 🔒 Privado - Vaciar carrito
@app.delete("/carrito/vaciar")
def vaciar_carrito(
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    usuario_id = token_valido.get("usuario_id")
    crud.vaciar_carrito(db, usuario_id)
    return {"mensaje": "Carrito vaciado correctamente"}