from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class ItemIn(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    items: list[ItemIn] = Field(min_length=1)


class ItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    
    model_config = {"from_attributes": True}


class PedidoOut(BaseModel):
    id: int
    usuario_id: int
    estado: str
    total: Decimal
    creado_en: datetime
    items: list[ItemOut]
    
    model_config = {"from_attributes": True}


class SolicitudOut(BaseModel):
    id: int
    codigo: str
    pedido_id: int
    creada_en: datetime
    
    model_config = {"from_attributes": True}