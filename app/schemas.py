from pydantic import BaseModel
from typing import Optional

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_final: float  # 👈 Cambiá de 'precio' a 'precio_final'
    en_stock: bool = True
    imagen_url: Optional[str] = None
    categoria_id: int
    cuotas_cantidad: int = 0  # 👈 NUEVO
    cuotas_valor: float = 0.0  # 👈 NUEVO
    garantia_meses: int = 0    # 👈 NUEVO

class ProductoResponse(ProductoCreate):
    id: int

    class Config:
        from_attributes = True