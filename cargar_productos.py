# cargar_productos.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Categoria, Producto

db = SessionLocal()

# Datos de las categorías y productos
categorias_data = [
    {"nombre": "Jugos Naturales"},
    {"nombre": "Jugos Detox"},
    {"nombre": "Limonadas"}
]

productos_data = [
    {
        "nombre": "Jugo de Naranja Natural",
        "descripcion": "100% naranja exprimida, sin conservantes ni azúcares añadidos.",
        "precio": 4500,
        "en_stock": True,
        "imagen_url": "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400",
        "categoria_nombre": "Jugos Naturales"
    },
    {
        "nombre": "Jugo Tropical",
        "descripcion": "Exótica combinación de ananá, mango y maracuyá.",
        "precio": 5200,
        "en_stock": True,
        "imagen_url": "https://images.unsplash.com/photo-1623066454793-9c4f13c2e6a6?w=400",
        "categoria_nombre": "Jugos Naturales"
    },
    {
        "nombre": "Jugo Detox Verde",
        "descripcion": "Mezcla revitalizante de manzana, pepino, espinaca y limón.",
        "precio": 5500,
        "en_stock": True,
        "imagen_url": "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400",
        "categoria_nombre": "Jugos Detox"
    },
    {
        "nombre": "Jugo de Frutilla y Banana",
        "descripcion": "Bebida dulce y energética.",
        "precio": 5000,
        "en_stock": True,
        "imagen_url": "https://images.unsplash.com/photo-1600271886742-f0496a5a3d46?w=400",
        "categoria_nombre": "Jugos Naturales"
    },
    {
        "nombre": "Limonada con Menta",
        "descripcion": "Refrescante para días calurosos.",
        "precio": 4800,
        "en_stock": True,
        "imagen_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400",
        "categoria_nombre": "Limonadas"
    }
]

try:
    # 1. Crear categorías (si no existen)
    categorias_creadas = {}
    for cat_data in categorias_data:
        categoria = db.query(Categoria).filter(Categoria.nombre == cat_data["nombre"]).first()
        if not categoria:
            categoria = Categoria(nombre=cat_data["nombre"])
            db.add(categoria)
            db.commit()
            db.refresh(categoria)
            print(f"✅ Categoría '{categoria.nombre}' creada con ID {categoria.id}")
        else:
            print(f"ℹ️ Categoría '{categoria.nombre}' ya existe (ID: {categoria.id})")
        categorias_creadas[cat_data["nombre"]] = categoria.id

    # 2. Crear productos
    for prod_data in productos_data:
        categoria_id = categorias_creadas.get(prod_data["categoria_nombre"])
        if not categoria_id:
            print(f"❌ Categoría '{prod_data['categoria_nombre']}' no encontrada")
            continue
        
        producto = Producto(
            nombre=prod_data["nombre"],
            descripcion=prod_data["descripcion"],
            precio=prod_data["precio"],
            en_stock=prod_data["en_stock"],
            imagen_url=prod_data["imagen_url"],
            categoria_id=categoria_id
        )
        db.add(producto)
        db.commit()
        db.refresh(producto)
        print(f"✅ Producto '{producto.nombre}' creado con ID {producto.id}")

    print("\n🎉 ¡Todos los productos de FrutiMix han sido cargados exitosamente!")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()