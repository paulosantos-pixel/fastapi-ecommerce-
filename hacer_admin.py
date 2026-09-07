# hacer_admin.py - Ejecutá esto una sola vez
import sys
import os

# Agregar la carpeta actual al path para que encuentre los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Usuario

db = SessionLocal()

try:
    # Buscar tu usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == "paulosantos@iresm.edu.ar").first()
    
    if usuario:
        usuario.es_admin = True
        db.commit()
        print(f"✅ {usuario.email} ahora es administrador")
        print(f"📊 ID: {usuario.id}, Nombre: {usuario.nombre}, Admin: {usuario.es_admin}")
    else:
        print("❌ Usuario no encontrado")
        print("📋 Usuarios registrados:")
        for u in db.query(Usuario).all():
            print(f"   - {u.email}")
finally:
    db.close()