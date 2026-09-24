from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Definir la base para los modelos
Base = declarative_base()

# Crear el motor de conexión (ejemplo con SQLite)
engine = create_engine("sqlite:///device_systems.db", echo=True)

# Crear la sesión
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)