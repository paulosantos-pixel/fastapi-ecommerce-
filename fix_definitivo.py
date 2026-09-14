from app.database import engine
from sqlalchemy import text

print("=" * 50)
print("DIAGNOSTICO Y ARREGLO DE LA TABLA productos")
print("=" * 50)

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='productos' ORDER BY ordinal_position"))
    print("\nColumnas ACTUALES de la tabla productos:")
    for row in result:
        print(f"   - {row[0]} ({row[1]})")

    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='productos' AND column_name IN ('precio', 'precio_final')"))
    cols_precio = [row[0] for row in result]
    print(f"\nColumnas de precio encontradas: {cols_precio}")

    if 'precio' in cols_precio and 'precio_final' not in cols_precio:
        print("\n>> Renombrando precio a precio_final...")
        conn.execute(text("ALTER TABLE productos RENAME COLUMN precio TO precio_final"))
        conn.commit()
        print("LISTO! La columna se renombro correctamente.")
    elif 'precio_final' in cols_precio and 'precio' not in cols_precio:
        print("\nLa columna precio_final YA EXISTE. No hay que hacer nada.")
    elif 'precio' in cols_precio and 'precio_final' in cols_precio:
        print("\nExisten AMBAS columnas. Eliminando precio...")
        conn.execute(text("ALTER TABLE productos DROP COLUMN precio"))
        conn.commit()
        print("Columna precio eliminada.")
    else:
        print("\nNo existe ninguna columna de precio. Creando precio_final...")
        conn.execute(text("ALTER TABLE productos ADD COLUMN precio_final FLOAT"))
        conn.commit()
        print("Columna precio_final creada.")

    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='productos' ORDER BY ordinal_position"))
    print("\nColumnas FINALES de la tabla productos:")
    for row in result:
        print(f"   - {row[0]}")

print("\n" + "=" * 50)
print("FIN DEL SCRIPT")
print("=" * 50)
