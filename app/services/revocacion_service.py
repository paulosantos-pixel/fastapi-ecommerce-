import secrets
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Pedido, Producto, SolicitudRevocacion

PLAZO_DIAS = 10  # Ley 24.240, art. 34


def generar_codigo() -> str:
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"ARR-{fecha}-{secrets.token_hex(3).upper()}"


def _fecha_aware(fecha):
    """Convierte fecha naive a aware para poder restar."""
    if fecha is None:
        return None
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha


def revocar(db: Session, usuario, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    
    if pedido is None or pedido.usuario_id != usuario.id:
        raise HTTPException(404, "No existe ese pedido")
    
    if pedido.estado == "cancelado":
        raise HTTPException(409, "Ya fue cancelado")
    
    creado = _fecha_aware(pedido.creado_en)
    ahora = datetime.now(timezone.utc)
    dias = (ahora - creado).days
    if dias > PLAZO_DIAS:
        raise HTTPException(409, f"El plazo de {PLAZO_DIAS} dias ya vencio")
    
    try:
        for item in pedido.items:
            producto = (db.query(Producto)
                        .filter(Producto.id == item.producto_id)
                        .with_for_update()
                        .first())
            if producto:
                producto.stock += item.cantidad
        
        pedido.estado = "cancelado"
        
        solicitud = SolicitudRevocacion(
            codigo=generar_codigo(),
            pedido_id=pedido.id,
            usuario_id=usuario.id,
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud
    except Exception:
        db.rollback()
        raise