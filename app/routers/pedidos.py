from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import Usuario, Pedido
from app.schemas import PedidoCreate, PedidoOut, SolicitudOut, PedidoEstadoUpdate, PedidoDelete
from app.services import pedido_service, revocacion_service
from app.core.security import verificar_password

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoOut, status_code=201)
def checkout(datos: PedidoCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return pedido_service.crear_pedido(db, usuario, datos)

@router.get("/mios", response_model=list[PedidoOut])
def mis_pedidos(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Pedido).filter(Pedido.usuario_id == usuario.id).order_by(Pedido.creado_en.desc()).all()

@router.get("/todos", response_model=list[PedidoOut])
def todos_los_pedidos(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.rol != "admin":
        raise HTTPException(403, "Solo administradores")
    return db.query(Pedido).order_by(Pedido.creado_en.desc()).all()

@router.put("/{pedido_id}/estado", response_model=PedidoOut)
def actualizar_estado(pedido_id: int, datos: PedidoEstadoUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.rol != "admin":
        raise HTTPException(403, "Solo administradores")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    pedido.estado = datos.estado
    db.commit()
    db.refresh(pedido)
    return pedido

@router.delete("/{pedido_id}")
def eliminar_pedido(pedido_id: int, datos: PedidoDelete, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.rol != "admin":
        raise HTTPException(403, "Solo administradores")
    # Verificamos que la contraseña ingresada sea la del admin logueado
    if not verificar_password(datos.password, usuario.hashed_password):
        raise HTTPException(400, "Contraseña incorrecta. No se eliminó el pedido.")
    
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    db.delete(pedido)
    db.commit()
    return {"mensaje": "Pedido eliminado correctamente"}

@router.post("/{pedido_id}/revocacion", response_model=SolicitudOut, status_code=201)
def revocar_pedido(pedido_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return revocacion_service.revocar(db, usuario, pedido_id)

@router.get("/{pedido_id}", response_model=PedidoOut)
def detalle(pedido_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None or (pedido.usuario_id != usuario.id and usuario.rol != "admin"):
        raise HTTPException(404, "No existe ese pedido")
    return pedido