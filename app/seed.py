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
        print("[*] Borrando productos viejos...")
        db.query(models.ItemPedido).delete()
        db.query(models.Producto).delete()
        db.commit()

        admin_email = "admin@frutimix.com"
        if not db.query(models.Usuario).filter_by(email=admin_email).first():
            db.add(models.Usuario(
                nombre="Admin FrutiMix", email=admin_email,
                hashed_password=hash_password("admin1234"),
                rol="admin", activo=True, acepto_tratamiento=True,
                fecha_consentimiento=datetime.now(timezone.utc)
            ))
            db.commit()

        cat = db.query(models.Categoria).filter_by(nombre="Jugos").first()
        if not cat:
            cat = models.Categoria(nombre="Jugos")
            db.add(cat)
            db.commit()

        # IMÁGENES DE PEXELS (A PRUEBA DE BALAS)
        jugos = [
            {"nombre": "Jugo Detox Verde", "descripcion": "Espinaca, apio y manzana verde.", "precio_final": 1700.0, "stock": 10, "imagen_url": "https://images.pexels.com/photos/2109099/pexels-photo-2109099.jpeg?auto=compress&cs=tinysrgb&w=600"},
            {"nombre": "Jugo de Naranja", "descripcion": "100% natural, prensado en frío.", "precio_final": 1500.0, "stock": 12, "imagen_url": "https://images.pexels.com/photos/1337825/pexels-photo-1337825.jpeg?auto=compress&cs=tinysrgb&w=600"},
            {"nombre": "Jugo Tropical", "descripcion": "Mango, ananá y maracuyá.", "precio_final": 1600.0, "stock": 8, "imagen_url": "https://images.pexels.com/photos/1233319/pexels-photo-1233319.jpeg?auto=compress&cs=tinysrgb&w=600"},
            {"nombre": "Licuado de Frutilla", "descripcion": "Frutillas frescas con leche y un toque de miel.", "precio_final": 1800.0, "stock": 15, "imagen_url": "https://images.pexels.com/photos/1132558/pexels-photo-1132558.jpeg?auto=compress&cs=tinysrgb&w=600"},
            {"nombre": "Batido de Chocolate", "descripcion": "Cacao puro, plátano y avena.", "precio_final": 1900.0, "stock": 10, "imagen_url": "https://images.pexels.com/photos/1300589/pexels-photo-1300589.jpeg?auto=compress&cs=tinysrgb&w=600"},
            {"nombre": "Limonada Artesanal", "descripcion": "Limón, menta y jengibre.", "precio_final": 1400.0, "stock": 20, "imagen_url": "https://images.pexels.com/photos/96974/pexels-photo-96974.jpeg?auto=compress&cs=tinysrgb&w=600"},
        ]

        for j in jugos:
            db.add(models.Producto(
                nombre=j["nombre"], descripcion=j["descripcion"],
                precio_final=j["precio_final"], stock=j["stock"],
                imagen_url=j["imagen_url"], categoria_id=cat.id, en_stock=True
            ))
        db.commit()
        print(">>> SEEDING COMPLETADO: 6 productos con imágenes de Pexels <<<")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()