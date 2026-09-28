from pydantic import BaseModel
from typing import Optional


class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_final: float
    en_stock: bool = True
    imagen_url: Optional[str] = None
    categoria_id: Optional[int] = None
    cuotas_cantidad: int = 0
    cuotas_valor: float = 0.0
    garantia_meses: int = 0


class ProductoOut(ProductoCreate):
    id: int
    
    class Config:
        from_attributes = True


class CategoriaCreate(BaseModel):
    nombre: str


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True


class CarritoItemCreate(BaseModel):
    producto_id: int
    cantidad: int = 1


class CarritoItemResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    
    class Config:
        from_attributes = True


class CarritoResponse(BaseModel):
    id: int
    usuario_id: int
    items: list[CarritoItemResponse]
    
    class Config:
        from_attributes = True