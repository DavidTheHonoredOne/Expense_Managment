from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Obtiene la URL. Si no existe, lanza un error para avisarte.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No se encontró la variable DATABASE_URL en el archivo .env")

# Configuración del motor de base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener la sesión (se usará en cada petición)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()