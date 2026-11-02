import secrets
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas import ProductoCreate, ProductoOut
from app.services import productos as productos_service
from app.utils.archivos import parece_imagen
from app import crud
from app.models import Producto, Usuario

router = APIRouter(prefix="/productos", tags=["Productos"])

CARPETA = Path("uploads/productos")
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 2 * 1024 * 1024  # 2 MB


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    skip: int = 0,
    limit: int = 10,
    nombre: str | None = None,
    precio_max: float | None = None,
    db: Session = Depends(get_db),
):
    return productos_service.listar_productos(db, skip, limit, nombre, precio_max)


@router.post("/", response_model=ProductoOut, status_code=201)
def agregar_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    return productos_service.crear_producto(db, producto)


@router.post("/{producto_id}/imagen", response_model=ProductoOut)
async def subir_imagen(
    producto_id: int,
    archivo: UploadFile = File(...),
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(404, "No existe ese producto")
    
    ext = Path(archivo.filename or "").suffix.lower()
    if ext not in EXTENSIONES:
        raise HTTPException(415, f"Formato no permitido. Use: {', '.join(EXTENSIONES)}")
    
    contenido = await archivo.read()
    if len(contenido) > MAX_BYTES:
        raise HTTPException(413, "Maximo 2 MB")
    
    if not parece_imagen(contenido):
        raise HTTPException(415, "El archivo no es una imagen valida")
    
    nombre = f"{producto_id}-{secrets.token_hex(8)}{ext}"
    CARPETA.mkdir(parents=True, exist_ok=True)
    (CARPETA / nombre).write_bytes(contenido)
    
    producto.imagen_url = f"/static/productos/{nombre}"
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: ProductoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    producto = crud.actualizar_producto(db, producto_id, datos)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.delete("/{producto_id}")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    producto = crud.eliminar_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}