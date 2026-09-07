# crear_tablas.py
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app import models

print("🔧 Conectando a la base de datos...")
print("📋 Creando tablas...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")
    
    # Verificar con SQL que las tablas existen
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n📊 Tablas existentes en la base de datos:")
    for table in tables:
        print(f"   - {table}")
        
except Exception as e:
    print(f"❌ Error al crear las tablas: {e}")
    print("\n💡 Posibles soluciones:")
    print("1. Verificá que PostgreSQL esté corriendo")
    print("2. Revisá la contraseña en app/database.py")
    print("3. Verificá que la base de datos 'ecommerce_db' exista")