from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión a la base de datos
DATABASE_URL = "sqlite:///device_systems.db"

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Crear la sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()