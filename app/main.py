from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
# Importamos lo nuevo de la seguridad
import auth 

app = FastAPI()

# 🔑 RUTA NUEVA: El usuario pone cualquier usuario/contraseña y le damos su token
@app.post("/login")
def login(usuario: str, contrasenia: str):
    # Una validación simple de simulación como pide tu guía
    if usuario == "admin" and contrasenia == "1234":
        token = auth.crear_token_acceso(usuario)
        return {"token_acceso": token, "tipo_token": "bearer"}
    raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")


@app.get("/productos", response_model=list[schemas.ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return crud.obtener_productos(db)


# 🔒 RUTA PROTEGIDA: Ahora pide Depends(auth.verificar_token) obligatoriamente
@app.post("/productos", response_model=schemas.ProductoCreate)
def agregar_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db), token_valido: dict = Depends(auth.verificar_token)):
    return crud.crear_producto(db, producto)


@app.put("/productos/{id}", response_model=schemas.ProductoCreate)
def actualizar_producto(producto_id: int, datos: schemas.ProductoCreate, db: Session = Depends(get_db)):
    producto = crud.actualizar_producto(db, producto_id, datos)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.delete("/productos/{id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = crud.eliminar_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}


@app.post("/categorias", response_model=schemas.CategoriaResponse)
def agregar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    return crud.crear_categoria(db, categoria)


@app.get("/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.obtener_categoria(db)