# backend/tests/test_tp_santos.py
from tests.conftest import registrar, token_de

def test_bt2_visitante_recibe_401(client):
    r = client.post("/productos/", json={"nombre": "x", "precio_final": 1.0, "stock": 1})
    assert r.status_code == 401

def test_bt2_cliente_no_puede_crear_producto(client, cliente):
    r = client.post("/productos/", headers=cliente, json={"nombre": "x", "precio_final": 1.0, "stock": 1})
    assert r.status_code == 403

def test_bt9_arrepentimiento_email_no_coincide(client, cliente, producto):
    # Crea un pedido
    r = client.post("/pedidos/", headers=cliente, json={"items": [{"producto_id": producto["id"], "cantidad": 1}]})
    pedido_id = r.json()["id"]
    
    # Pide arrepentimiento con un email que NO es el del cliente
    r2 = client.post("/arrepentimiento/", json={"email": "otro@prueba.com", "pedido_id": pedido_id})
    assert r2.status_code == 201
    assert r2.json().get("codigo") # Respuesta uniforme
    
    # Verifica que el stock NO volvió (no se canceló)
    prod_actualizado = next(p for p in client.get("/productos/").json() if p["id"] == producto["id"])
    assert prod_actualizado["stock"] == 4 # Porque el fixture producto tiene stock 5