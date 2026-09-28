import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import Usuario, Pedido, SolicitudRevocacion

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _armar_datos(db: Session, usuario: Usuario) -> dict:
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    solicitudes = db.query(SolicitudRevocacion).filter(
        SolicitudRevocacion.usuario_id == usuario.id
    ).all()
    return {
        "titular": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "alta": usuario.created_at,
        },
        "consentimiento": {
            "otorgado": usuario.acepto_tratamiento,
            "fecha": usuario.fecha_consentimiento,
        },
        "pedidos": [
            {"id": p.id, "fecha": p.creado_en, "total": p.total, "estado": p.estado}
            for p in pedidos
        ],
        "solicitudes_revocacion": [
            {"codigo": s.codigo, "pedido_id": s.pedido_id, "creada_en": s.creada_en}
            for s in solicitudes
        ],
    }


@router.get("/me/datos")
def mis_datos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _armar_datos(db, usuario)


@router.get("/me/exportar")
def exportar_datos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    datos = _armar_datos(db, usuario)
    contenido = json.dumps(datos, default=str, ensure_ascii=False, indent=2)
    return Response(
        content=contenido,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="mis-datos-{usuario.id}.json"'
        },
    )


@router.delete("/me")
def eliminar_mi_cuenta(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuario.nombre = "Usuario dado de baja"
    usuario.email = f"baja-{usuario.id}@anonimo.local"
    usuario.hashed_password = "!"
    usuario.acepto_tratamiento = False
    usuario.activo = False
    usuario.fecha_baja = datetime.now(timezone.utc)
    db.commit()
    return {"detalle": "Tu cuenta fue dada de baja y tus datos personales se eliminaron."}