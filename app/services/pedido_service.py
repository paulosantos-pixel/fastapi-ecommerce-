from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Producto, Pedido, ItemPedido
from app.schemas import PedidoCreate


def crear_pedido(db: Session, usuario, datos: PedidoCreate):
    pedido = Pedido(usuario_id=usuario.id, estado="pendiente")
    total = Decimal("0")
    
    try:
        for item in datos.items:
            p = (db.query(Producto)
                 .filter(Producto.id == item.producto_id)
                 .with_for_update()
                 .first())
            
            if p is None:
                raise HTTPException(404, f"Producto {item.producto_id} no existe")
            
            if p.stock < item.cantidad:
                raise HTTPException(
                    409,
                    f"Sin stock de {p.nombre}: quedan {p.stock} unidades"
                )
            
            p.stock -= item.cantidad
            total += p.precio_final * item.cantidad
            
            pedido.items.append(ItemPedido(
                producto_id=p.id,
                cantidad=item.cantidad,
                precio_unitario=p.precio_final,
            ))
        
        pedido.total = total
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        return pedido
    
    except Exception:
        db.rollback()
        raise