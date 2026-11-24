import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.dependencies import get_db
from app.database import Base
from app import models

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SesionPrueba = sessionmaker(bind=engine, autoflush=False)

def get_db_prueba():
    with SesionPrueba() as db:
        yield db

@pytest.fixture
def client():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = get_db_prueba
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def registrar(client, email="cliente@prueba.com", password="clave12345"):
    r = client.post("/auth/register", json={
        "nombre": "Test", 
        "email": email, 
        "password": password,
        "acepto_tratamiento": True  # <-- Agregamos esto para cumplir la ley
    })
    assert r.status_code == 201, r.text # Agregamos r.text para ver el error si falla de nuevo
    return email, password

def token_de(client, email, password):
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

@pytest.fixture
def cliente(client):
    email, pwd = registrar(client)
    return token_de(client, email, pwd)

@pytest.fixture
def admin(client):
    email, pwd = registrar(client, email="admin@prueba.com")
    with SesionPrueba() as db:
        u = db.query(models.Usuario).filter_by(email=email).one()
        u.rol = "admin"
        db.commit()
    return token_de(client, email, pwd)

@pytest.fixture
def producto(client, admin):
    r = client.post("/productos/", headers=admin, json={
        "nombre": "Mate", "precio_final": 1000.0, "stock": 5
    })
    return r.json()