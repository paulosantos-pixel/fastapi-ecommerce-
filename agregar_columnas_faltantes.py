from app.database import engine
from sqlalchemy import text

print("=" * 50)
print("AGREGANDO COLUMNAS FALTANTES A productos")
print("=" * 50)

with engine.connect() as conn:
    # Agregar cuotas_cantidad
    try:
        conn.execute(text("ALTER TABLE productos ADD COLUMN cuotas_cantidad INTEGER DEFAULT 0"))
        conn.commit()
        print("OK: cuotas_cantidad agregada")
    except Exception as e:
        print(f"cuotas_cantidad: {e}")
        conn.rollback()

    # Agregar cuotas_valor
    try:
        conn.execute(text("ALTER TABLE productos ADD COLUMN cuotas_valor FLOAT DEFAULT 0.0"))
        conn.commit()
        print("OK: cuotas_valor agregada")
    except Exception as e:
        print(f"cuotas_valor: {e}")
        conn.rollback()

    # Agregar garantia_meses
    try:
        conn.execute(text("ALTER TABLE productos ADD COLUMN garantia_meses INTEGER DEFAULT 0"))
        conn.commit()
        print("OK: garantia_meses agregada")
    except Exception as e:
        print(f"garantia_meses: {e}")
        conn.rollback()

    # Verificar
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='productos' ORDER BY ordinal_position"))
    print("\nColumnas FINALES de productos:")
    for row in result:
        print(f"   - {row[0]}")

print("\n" + "=" * 50)
print("LISTO! Ahora proba GET /productos en Swagger")
print("=" * 50)
