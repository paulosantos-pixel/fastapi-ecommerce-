from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app import schemas, auth, crud
from app.services import productos as productos_service

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=list[schemas.ProductoOut])
def listar_productos(
    skip: int = 0,
    limit: int = 10,
    nombre: str | None = None,
    precio_max: float | None = None,
    db: Session = Depends(get_db),
):
    return productos_service.listar_productos(db, skip, limit, nombre, precio_max)

@router.post("/", response_model=schemas.ProductoOut)
def agregar_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado. Solo administradores pueden crear productos.")
    return productos_service.crear_producto(db, producto)

@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado.")
    producto = crud.actualizar_producto(db, producto_id, datos)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.delete("/{producto_id}")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    token_valido: dict = Depends(auth.verificar_token)
):
    if not token_valido.get("es_admin"):
        raise HTTPException(status_code=403, detail="No autorizado.")
    producto = crud.eliminar_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}