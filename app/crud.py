from sqlalchemy.orm import Session
from models import Producto, Categoria
from schemas import ProductoCreate, CategoriaCreate


def crear_producto(db: Session, producto: ProductoCreate):
    db_producto = Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def obtener_productos(db: Session):
    return db.query(Producto).all()


def obtener_producto(db: Session, producto_id: int):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def actualizar_producto(db: Session, producto_id: int, datos: ProductoCreate):
    producto = obtener_producto(db, producto_id)
    if producto:
        producto.nombre = datos.nombre
        producto.precio = datos.precio
        producto.en_stock = datos.en_stock
        producto.categoria_id = datos.categoria_id
        db.commit()
        db.refresh(producto)
    return producto


def eliminar_producto(db: Session, producto_id: int):
    producto = obtener_producto(db, producto_id)
    
    if producto:
        db.delete(producto)
        db.commit()
    return producto


##### Categoria ###


def crear_categoria(db: Session, categoria: CategoriaCreate):
    db_categoria = Categoria(nombre=categoria.nombre)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


def obtener_categoria(db: Session):
    return db.query(Categoria).all()