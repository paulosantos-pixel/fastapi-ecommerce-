from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.dependencies import get_db, get_current_user, require_admin
from app import crud, schemas
from app.models import Categoria, Producto
from app.routers import productos, auth, pedidos, usuarios, arrepentimiento

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clase 12: Compresión GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

Path("uploads/productos").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

DEMO_DIR = Path("app/static/demo")
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# Clase 12: Caché para las imágenes estáticas
class StaticConCache(StaticFiles):
    async def get_response(self, path, scope):
        r = await super().get_response(path, scope)
        if r.status_code == 200:
            r.headers["Cache-Control"] = "public, max-age=2592000, immutable"
        return r

app.mount("/static", StaticConCache(directory="uploads"), name="static")
app.mount("/demo", StaticConCache(directory=str(DEMO_DIR)), name="demo")

@app.get("/")
def raiz():
    return {"status": "ok", "app": settings.PROJECT_NAME}

@app.get("/salud")
def salud(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"estado": "ok", "base": "ok"}

@app.get("/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.obtener_categorias(db)

@app.post("/categorias", response_model=schemas.CategoriaResponse, status_code=201)
def agregar_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    return crud.crear_categoria(db, categoria)

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).first()
    if productos_asociados:
        raise HTTPException(status_code=400, detail="No se puede eliminar la categoria porque tiene productos asociados")
    db.delete(categoria)
    db.commit()
    return {"mensaje": f"Categoria '{categoria.nombre}' eliminada correctamente"}

@app.get("/carrito", response_model=schemas.CarritoResponse)
def ver_carrito(db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    return crud.obtener_carrito(db, usuario.id)

@app.post("/carrito/items", response_model=schemas.CarritoItemResponse)
def agregar_al_carrito(
    item: schemas.CarritoItemCreate,
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user),
):
    return crud.agregar_item_carrito(db, usuario.id, item)

@app.delete("/carrito/items/{item_id}")
def eliminar_del_carrito(
    item_id: int,
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user),
):
    item = crud.eliminar_item_carrito(db, usuario.id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"mensaje": "Item eliminado del carrito"}

@app.delete("/carrito/vaciar")
def vaciar_carrito(db: Session = Depends(get_db), usuario = Depends(get_current_user)):
    crud.vaciar_carrito(db, usuario.id)
    return {"mensaje": "Carrito vaciado correctamente"}

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(usuarios.router)
app.include_router(arrepentimiento.router)