import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app import models
from app.core.security import hash_password

def seed_all():
    db = SessionLocal()
    try:
        # 1. Borrar los productos viejos (Manzana, Banana, etc)
        print("[*] Borrando productos viejos...")
        db.query(models.ItemPedido).delete() # Borrar items de pedidos viejos primero
        db.query(models.Producto).delete()
        db.commit()

        # 2. Crear Admin
        admin_email = "admin@frutimix.com"
        if not db.query(models.Usuario).filter_by(email=admin_email).first():
            db.add(models.Usuario(
                nombre="Admin FrutiMix", email=admin_email,
                hashed_password=hash_password("admin1234"),
                rol="admin", activo=True, acepto_tratamiento=True,
                fecha_consentimiento=datetime.now(timezone.utc)
            ))
            db.commit()

        # 3. Crear Categoría
        cat = db.query(models.Categoria).filter_by(nombre="Jugos").first()
        if not cat:
            cat = models.Categoria(nombre="Jugos")
            db.add(cat)
            db.commit()

        # 4. Crear los Jugos
        jugos = [
            {"nombre": "Jugo Detox Verde", "descripcion": "Espinaca, apio y manzana verde.", "precio_final": 1700.0, "stock": 10, "imagen_url": "/demo/detox.jpg"},
            {"nombre": "Jugo de Naranja", "descripcion": "100% natural, prensado en frío.", "precio_final": 1500.0, "stock": 12, "imagen_url": "/demo/naranja.jpg"},
            {"nombre": "Jugo Tropical", "descripcion": "Mango, ananá y maracuyá.", "precio_final": 1600.0, "stock": 8, "imagen_url": "/demo/tropical.jpg"},
        ]

        for j in jugos:
            db.add(models.Producto(
                nombre=j["nombre"], descripcion=j["descripcion"],
                precio_final=j["precio_final"], stock=j["stock"],
                imagen_url=j["imagen_url"], categoria_id=cat.id, en_stock=True
            ))
        db.commit()
        print(">>> SEEDING COMPLETADO: Jugos creados con imágenes <<<")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()