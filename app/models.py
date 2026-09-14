from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    contrasenia = Column(String)  # Guardar hasheada en producción
    es_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    carrito = relationship("Carrito", back_populates="usuario", uselist=False)
    pedidos = relationship("Pedido", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    
    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    precio_final = Column(Float)
    en_stock = Column(Boolean, default=True)
    imagen_url = Column(String, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    cuotas_cantidad = Column(Integer, default=0)
    cuotas_valor = Column(Float, default=0.0)
    garantia_meses = Column(Integer, default=0)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    items_carrito = relationship("CarritoItem", back_populates="producto")


class Carrito(Base):
    __tablename__ = "carritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="carrito")
    items = relationship("CarritoItem", back_populates="carrito")


class CarritoItem(Base):
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True)
    carrito_id = Column(Integer, ForeignKey("carritos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    
    # Relaciones
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto", back_populates="items_carrito")


# ==================== PEDIDO ====================
class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    estado = Column(String, default="pendiente")  # pendiente, pagado, enviado, entregado
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido")


# ==================== ITEM_PEDIDO ====================
class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float, default=0.0)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")