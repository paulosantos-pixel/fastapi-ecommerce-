"""
Script de siembra (Seeder) para la base de datos de FrutiMix.
Crea: Admin, Cliente, Categoría, Productos y un Pedido de muestra.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app import models
from app.core.security import hash_password


def seed_usuarios(db: Session) -> dict:
    print("[*] Verificando usuarios iniciales...")

    # Admin
    admin_email = "admin@frutimix.com"
    admin_password = "admin1234"

    admin = db.query(models.Usuario).filter(models.Usuario.email == admin_email).first()
    if not admin:
        admin = models.Usuario(
            nombre="Admin FrutiMix",
            email=admin_email,
            hashed_password=hash_password(admin_password),
            rol="admin", # Tu modelo usa "admin"
            activo=True,
            acepto_tratamiento=True,
            fecha_consentimiento=datetime.now(timezone.utc),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"  [+] Usuario Admin creado: {admin_email}")
    else:
        print(f"  [i] Usuario Admin ya existe: {admin_email}")

    # Cliente
    cliente_email = "cliente@frutimix.com"
    cliente_password = "cliente1234"

    cliente = db.query(models.Usuario).filter(models.Usuario.email == cliente_email).first()
    if not cliente:
        cliente = models.Usuario(
            nombre="Cliente Demo",
            email=cliente_email,
            hashed_password=hash_password(cliente_password),
            rol="customer", # ¡OJO! Tu modelo usa "customer", no "cliente"
            activo=True,
            acepto_tratamiento=True,
            fecha_consentimiento=datetime.now(timezone.utc),
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        print(f"  [+] Usuario Cliente creado: {cliente_email}")
    else:
        print(f"  [i] Usuario Cliente ya existe: {cliente_email}")

    return {"admin": admin, "cliente": cliente}


def seed_productos(db: Session) -> list:
    print("[*] Verificando categorías y catálogo de productos...")

    # Tu modelo exige una categoría, la creamos primero
    cat = db.query(models.Categoria).filter_by(nombre="Jugos Naturales").first()
    if not cat:
        cat = models.Categoria(nombre="Jugos Naturales")
        db.add(cat)
        db.commit()
        db.refresh(cat)

    productos_iniciales = [
        {
            "nombre": "Jugo Detox Verde",
            "descripcion": "Jugo detox con verduras, espinaca y hierbas frescas. Ideal para depurar.",
            "precio_final": 1700.00, # Tu modelo usa "precio_final"
            "stock": 10,
            "imagen_url": None, # Le ponemos None para que se vea el cartel de "Sin Imagen"
        },
        {
            "nombre": "Jugo de Naranja Natural",
            "descripcion": "Naranja 100% natural, prensada en frio. Vitamina C pura para arrancar el dia.",
            "precio_final": 1500.00,
            "stock": 12,
            "imagen_url": None,
        },
        {
            "nombre": "Jugo Tropical Mix",
            "descripcion": "Mezcla tropical de mango, anana y maracuya. Dulzura natural sin azucar agregada.",
            "precio_final": 1600.00,
            "stock": 8,
            "imagen_url": None,
        },
    ]

    productos_creados = []
    for item in productos_iniciales:
        prod = db.query(models.Producto).filter(models.Producto.nombre == item["nombre"]).first()
        if not prod:
            prod = models.Producto(
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                precio_final=item["precio_final"],
                stock=item["stock"],
                imagen_url=item["imagen_url"],
                categoria_id=cat.id, # Asignamos la categoría
                en_stock=True,
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
            print(f"  [+] Producto creado: {prod.nombre} - ${prod.precio_final}")
        else:
            print(f"  [i] Producto ya existe: {prod.nombre}")
        productos_creados.append(prod)

    return productos_creados


def seed_pedidos(db: Session, cliente: models.Usuario, productos: list):
    print("[*] Verificando pedidos de muestra...")
    if not cliente or not productos:
        return

    pedido_existente = db.query(models.Pedido).filter(models.Pedido.usuario_id == cliente.id).first()
    if not pedido_existente and len(productos) >= 2:
        prod1 = productos[0]  # Detox
        prod2 = productos[1]  # Naranja

        subtotal1 = prod1.precio_final * 1
        subtotal2 = prod2.precio_final * 2
        total = subtotal1 + subtotal2

        nuevo_pedido = models.Pedido(
            usuario_id=cliente.id,
            total=total,
            estado="pagado",
            creado_en=datetime.now(timezone.utc),
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)

        item1 = models.ItemPedido(
            pedido_id=nuevo_pedido.id,
            producto_id=prod1.id,
            cantidad=1,
            precio_unitario=prod1.precio_final,
        )
        item2 = models.ItemPedido(
            pedido_id=nuevo_pedido.id,
            producto_id=prod2.id,
            cantidad=2,
            precio_unitario=prod2.precio_final,
        )
        db.add_all([item1, item2])
        db.commit()
        print(f"  [+] Pedido de muestra creado (ID: {nuevo_pedido.id}) por un total de ${total}")
    else:
        print("  [i] Pedidos de muestra ya existentes o no requeridos.")


def seed_all():
    print("=" * 60)
    print(">>> INICIANDO PROCESO DE SEEDING DE BASE DE DATOS <<<")
    print("=" * 60)

    print("[*] Creando tablas en la base de datos si no existen...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tablas verificadas/creadas.")

    db = SessionLocal()
    try:
        usuarios = seed_usuarios(db)
        productos = seed_productos(db)
        seed_pedidos(db, usuarios.get("cliente"), productos)
        print("=" * 60)
        print(">>> SEEDING COMPLETADO EXITOSAMENTE <<<")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante el proceso de seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()