# clase2_demo.py
from pydantic import BaseModel
from typing import Optional

class Producto(BaseModel):
    id: int
    nombre: str
    precio_final: float
    cuotas_cantidad: int
    cuotas_valor: float
    garantia_meses: int
    stock: int
    descripcion: Optional[str] = None

# Lista en memoria con 3 productos de FrutiMix
productos_db = [
    Producto(
        id=1,
        nombre="Jugo de Naranja Natural",
        descripcion="100% naranja exprimida",
        precio_final=4500,
        cuotas_cantidad=3,
        cuotas_valor=1500,
        garantia_meses=0,
        stock=100
    ),
    Producto(
        id=2,
        nombre="Jugo Tropical",
        descripcion="Ananá, mango y maracuyá",
        precio_final=5200,
        cuotas_cantidad=3,
        cuotas_valor=1734,
        garantia_meses=0,
        stock=80
    ),
    Producto(
        id=3,
        nombre="Jugo Detox Verde",
        descripcion="Manzana, pepino, espinaca y limón",
        precio_final=5500,
        cuotas_cantidad=3,
        cuotas_valor=1834,
        garantia_meses=0,
        stock=60
    )
]

if __name__ == "__main__":
    print("📋 Productos en memoria:")
    for p in productos_db:
        print(f"   - {p.nombre}: ${p.precio_final} (stock: {p.stock})")