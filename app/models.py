from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, default="customer", nullable=False)
    acepto_tratamiento = Column(Boolean, default=False, nullable=False)
    fecha_consentimiento = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_baja = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    carrito = relationship("Carrito", back_populates="usuario", uselist=False)
    pedidos = relationship("Pedido", back_populates="usuario")
    solicitudes = relationship("SolicitudRevocacion", back_populates="usuario")


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
    precio_final = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    en_stock = Column(Boolean, default=True)
    imagen_url = Column(String, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    cuotas_cantidad = Column(Integer, default=0)
    cuotas_valor = Column(Float, default=0.0)
    garantia_meses = Column(Integer, default=0)
    
    categoria = relationship("Categoria", back_populates="productos")
    items_carrito = relationship("CarritoItem", back_populates="producto")


class Carrito(Base):
    __tablename__ = "carritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="carrito")
    items = relationship("CarritoItem", back_populates="carrito")


class CarritoItem(Base):
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True)
    carrito_id = Column(Integer, ForeignKey("carritos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, default=1)
    
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto", back_populates="items_carrito")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    estado = Column(String, default="pendiente", nullable=False)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    solicitudes = relationship("SolicitudRevocacion", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")


class SolicitudRevocacion(Base):
    __tablename__ = "solicitudes_revocacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    creada_en = Column(DateTime(timezone=True), server_default=func.now())
    
    pedido = relationship("Pedido", back_populates="solicitudes")
    usuario = relationship("Usuario", back_populates="solicitudes")