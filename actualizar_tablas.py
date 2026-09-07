# actualizar_tablas.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal

db = SessionLocal()

try:
    # Verificar si la columna existe
    result = db.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='productos' AND column_name='descripcion'
    """))
    
    exists = result.fetchone()
    
    if not exists:
        print("🔧 Agregando columna 'descripcion' a la tabla productos...")
        db.execute(text("ALTER TABLE productos ADD COLUMN descripcion VARCHAR"))
        db.commit()
        print("✅ Columna 'descripcion' agregada correctamente")
    else:
        print("✅ La columna 'descripcion' ya existe")
    
    # Verificar si la columna imagen_url existe
    result = db.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='productos' AND column_name='imagen_url'
    """))
    
    exists = result.fetchone()
    
    if not exists:
        print("🔧 Agregando columna 'imagen_url' a la tabla productos...")
        db.execute(text("ALTER TABLE productos ADD COLUMN imagen_url VARCHAR"))
        db.commit()
        print("✅ Columna 'imagen_url' agregada correctamente")
    else:
        print("✅ La columna 'imagen_url' ya existe")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()