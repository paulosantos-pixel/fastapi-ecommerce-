import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.dependencies import get_db
from app.models import Pedido, SolicitudRevocacion, Producto
from app.schemas import SolicitudOut

router = APIRouter(prefix="/arrepentimiento", tags=["Arrepentimiento"])

class ArrepentimientoIn(BaseModel):
    email: str
    pedido_id: int

@router.post("/", response_model=SolicitudOut, status_code=201)
def arrepentimiento_publico(datos: ArrepentimientoIn, db: Session = Depends(get_db)):
    codigo = f"ARR-{secrets.token_hex(3).upper()}"
    pedido = db.query(Pedido).filter(Pedido.id == datos.pedido_id).first()
    
    # Si el email coincide, cancelamos el pedido y devolvemos el stock
    if pedido and pedido.usuario.email == datos.email and pedido.estado != "cancelado":
        for item in pedido.items:
            prod = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if prod:
                prod.stock += item.cantidad
        pedido.estado = "cancelado"
    
    # Guardamos la solicitud (aunque el email no coincida, para dar respuesta uniforme)
    solicitud = SolicitudRevocacion(
        codigo=codigo, 
        pedido_id=datos.pedido_id, 
        usuario_id=pedido.usuario_id if pedido else None
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud