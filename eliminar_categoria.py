import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Categoria, Producto

db = SessionLocal()

try:
    # Buscar la categoría por nombre
    categoria = db.query(Categoria).filter(Categoria.nombre == "Electrodomésticos").first()
    
    if categoria:
        print(f"🔍 Categoría encontrada: ID {categoria.id} - {categoria.nombre}")
        
        # Verificar si tiene productos asociados
        productos = db.query(Producto).filter(Producto.categoria_id == categoria.id).first()
        
        if productos:
            print("❌ No se puede eliminar porque tiene productos asociados")
            print("📋 Primero eliminá los productos o cambiales la categoría")
            
            # Opción: Mostrar qué productos tiene
            todos = db.query(Producto).filter(Producto.categoria_id == categoria.id).all()
            for p in todos:
                print(f"   - Producto: {p.nombre} (ID: {p.id})")
        else:
            db.delete(categoria)
            db.commit()
            print(f"✅ Categoría '{categoria.nombre}' eliminada correctamente")
    else:
        print("❌ No se encontró la categoría 'Electrodomésticos'")
        print("📋 Categorías existentes:")
        for c in db.query(Categoria).all():
            print(f"   - ID: {c.id}, Nombre: {c.nombre}")
finally:
    db.close()