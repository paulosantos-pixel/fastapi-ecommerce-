from sqlalchemy.orm import Session
from app.models import Producto, Categoria, Usuario, Carrito, CarritoItem
from app.schemas import ProductoCreate
# ==================== USUARIOS ====================
def crear_usuario(db: Session, usuario: UsuarioCreate):
    db_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        contrasenia=usuario.contrasenia,  # ¡HASHEAR EN PRODUCCIÓN!
        es_admin=False
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Crear carrito automáticamente para el usuario
    carrito = Carrito(usuario_id=db_usuario.id)
    db.add(carrito)
    db.commit()
    
    return db_usuario

def obtener_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

# ==================== PRODUCTOS ====================
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
        producto.descripcion = datos.descripcion
        producto.precio = datos.precio
        producto.en_stock = datos.en_stock
        producto.imagen_url = datos.imagen_url
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

# ==================== CATEGORIAS ====================
def crear_categoria(db: Session, categoria: CategoriaCreate):
    db_categoria = Categoria(nombre=categoria.nombre)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

def obtener_categorias(db: Session):
    return db.query(Categoria).all()

# ==================== CARRITO ====================
def obtener_carrito(db: Session, usuario_id: int):
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario_id).first()
    if not carrito:
        carrito = Carrito(usuario_id=usuario_id)
        db.add(carrito)
        db.commit()
        db.refresh(carrito)
    return carrito

def agregar_item_carrito(db: Session, usuario_id: int, item: CarritoItemCreate):
    carrito = obtener_carrito(db, usuario_id)
    
    existing_item = db.query(CarritoItem).filter(
        CarritoItem.carrito_id == carrito.id,
        CarritoItem.producto_id == item.producto_id
    ).first()
    
    if existing_item:
        existing_item.cantidad += item.cantidad
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    nuevo_item = CarritoItem(
        carrito_id=carrito.id,
        producto_id=item.producto_id,
        cantidad=item.cantidad
    )
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    return nuevo_item

def eliminar_item_carrito(db: Session, usuario_id: int, item_id: int):
    carrito = obtener_carrito(db, usuario_id)
    item = db.query(CarritoItem).filter(
        CarritoItem.id == item_id,
        CarritoItem.carrito_id == carrito.id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return item

def vaciar_carrito(db: Session, usuario_id: int):
    carrito = obtener_carrito(db, usuario_id)
    db.query(CarritoItem).filter(CarritoItem.carrito_id == carrito.id).delete()
    db.commit()
    return carrito