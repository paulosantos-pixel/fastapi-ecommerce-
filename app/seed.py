import os
from app.database import SessionLocal
from app.models import Usuario, Categoria, Producto
from app.core.security import hash_password

def cargar_datos():
    db = SessionLocal()
    
    # 1. Crear Admin
    admin_email = "admin@frutimix.com"
    if not db.query(Usuario).filter_by(email=admin_email).first():
        admin = Usuario(
            nombre="Admin FrutiMix",
            email=admin_email,
            hashed_password=hash_password("admin1234"),
            rol="admin",
            acepto_tratamiento=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin creado: {admin_email} / admin1234")

    # 2. Crear Categoría
    cat = db.query(Categoria).filter_by(nombre="Frutas").first()
    if not cat:
        cat = Categoria(nombre="Frutas")
        db.add(cat)
        db.commit()

    # 3. Crear Productos (con y sin imagen para la Clase 10)
    productos = [
        {"nombre": "Manzana Roja", "precio_final": 1500.0, "stock": 10, "imagen_url": None},
        {"nombre": "Banana Ecuador", "precio_final": 800.0, "stock": 20, "imagen_url": None},
        {"nombre": "Frutilla", "precio_final": 2500.0, "stock": 5, "imagen_url": None}
    ]
    
    for p in productos:
        if not db.query(Producto).filter_by(nombre=p["nombre"]).first():
            nuevo = Producto(
                nombre=p["nombre"], 
                precio_final=p["precio_final"], 
                stock=p["stock"], 
                imagen_url=p["imagen_url"],
                categoria_id=cat.id
            )
            db.add(nuevo)
    
    db.commit()
    db.close()
    print("Productos de demo cargados.")

if __name__ == "__main__":
    cargar_datos()