def test_salud_responde_con_la_base(client):
    r = client.get("/salud")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok", "base": "ok"}

def test_cliente_no_puede_crear_producto(client, cliente):
    r = client.post("/productos/", headers=cliente, json={"nombre": "X", "precio_final": 1.0})
    assert r.status_code == 403

def test_sin_stock_da_409_y_no_toca_nada(client, cliente, producto):
    # Pide 6, pero hay 5
    r = client.post("/pedidos/", headers=cliente, json={"items": [{"producto_id": producto["id"], "cantidad": 6}]})
    assert r.status_code == 409
    
    # Como no hay GET /productos/{id}, buscamos el stock en la lista completa
    lista_productos = client.get("/productos/").json()
    prod_actualizado = next(p for p in lista_productos if p["id"] == producto["id"])
    
    # Verifica que el stock siga en 5
    assert prod_actualizado["stock"] == 5
    
def test_arrepentimiento_sin_sesion(client, cliente, producto):
    # Crea el pedido
    r_pedido = client.post("/pedidos/", headers=cliente, json={"items": [{"producto_id": producto["id"], "cantidad": 1}]})
    pedido_id = r_pedido.json()["id"]
    
    # Pide arrepentimiento sin token
    r = client.post("/arrepentimiento/", json={"email": "cliente@prueba.com", "pedido_id": pedido_id})
    assert r.status_code == 201
    assert r.json()["codigo"]

def test_archivo_trampa_da_415(client, admin, producto):
    TRAMPA = ("foto.png", b"esto es texto, no una imagen", "image/png")
    r = client.post(f"/productos/{producto['id']}/imagen", headers=admin, files={"archivo": TRAMPA})
    assert r.status_code == 415