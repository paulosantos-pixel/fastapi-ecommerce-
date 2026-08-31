# limpiar_productos.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Producto

db = SessionLocal()

try:
    # Contar productos antes de eliminar
    count = db.query(Producto).count()
    print(f"📊 Hay {count} productos en la base de datos.")
    
    if count > 0:
        # Mostrar qué productos hay
        print("📋 Productos a eliminar:")
        for p in db.query(Producto).all():
            print(f"   - ID: {p.id}, Nombre: {p.nombre}, Categoría ID: {p.categoria_id}")
        
        # Eliminar todos los productos
        db.query(Producto).delete()
        db.commit()
        print(f"✅ {count} productos eliminados correctamente")
    else:
        print("✅ No hay productos para eliminar")
        
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()