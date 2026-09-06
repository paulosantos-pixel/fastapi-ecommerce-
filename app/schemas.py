from pydantic import BaseModel
from typing import Optional

# ==================== PRODUCTOS ====================
class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_final: float
    en_stock: bool = True
    imagen_url: Optional[str] = None
    categoria_id: int
    cuotas_cantidad: int = 0
    cuotas_valor: float = 0.0
    garantia_meses: int = 0

class ProductoResponse(ProductoCreate):
    id: int

    class Config:
        from_attributes = True

# ==================== CATEGORIAS ====================
class CategoriaCreate(BaseModel):
    nombre: str

class CategoriaResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

# ==================== USUARIOS ====================
class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    contrasenia: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool

    class Config:
        from_attributes = True

# ==================== CARRITO ====================
class CarritoItemCreate(BaseModel):
    producto_id: int
    cantidad: int = 1

class CarritoItemResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    producto: ProductoResponse

    class Config:
        from_attributes = True
        
# app/schemas.py - Agregar al final
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool

    class Config:
        from_attributes = True