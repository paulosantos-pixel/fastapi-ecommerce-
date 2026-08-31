from .database import engine, Base # CAMBIO IMPORTANTE: Le puse un punto adelante
from .models import * # CAMBIO IMPORTANTE: Le puse un punto adelante

Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente")