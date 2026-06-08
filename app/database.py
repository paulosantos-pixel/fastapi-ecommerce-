from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Fijate que se llame EXACTAMENTE igual arriba y abajo: DATABASE_URL
DATABASE_URL = "postgresql://postgres:mazzini180@localhost:5432/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionmLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()