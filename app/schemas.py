from pydantic import BaseModel
from typing import Optional, List

# ==================== USUARIOS ====================
class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    contrasenia: str

class UsuarioLogin(BaseModel):
    email: str
    contrasenia: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool

    class Config:
        from_attributes = True

# ==================== PRODUCTOS ====================
class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    en_stock: bool = True
    imagen_url: Optional[str] = None
    categoria_id: int

class ProductoResponse(ProductoCreate):
    id: int

    class Config:
        from_attributes = True

# ==================== CATEGORIAS ====================
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

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

class CarritoResponse(BaseModel):
    id: int
    usuario_id: int
    items: List[CarritoItemResponse]

    class Config:
        from_attributes = True

# ==================== TOKEN ====================
class TokenResponse(BaseModel):
    token_acceso: str
    tipo_token: str = "bearer"