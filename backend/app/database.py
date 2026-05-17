from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

"""
DATABASE CONFIGURATION MODULE
-----------------------------
Modul ini mengelola koneksi database dan konfigurasi lingkungan.
Menggunakan Pydantic Settings untuk membaca variabel dari file .env.
"""

class Settings(BaseSettings):
    """
    Class Settings
    --------------
    Membaca variabel lingkungan secara otomatis. 
    Jika file .env ada, maka nilai di dalamnya akan diutamakan.
    """
    # Default URL (fallback)
    DATABASE_URL: str = "postgresql://postgres:123@localhost:5432/seatrack_db"
    
    # Konfigurasi untuk membaca file .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Inisialisasi settings
settings = Settings()

# 1. Engine Creation
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# 2. Session Configuration
sessionmaker_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base Class
Base = declarative_base()

def get_db():
    """
    Dependency Generator
    --------------------
    Menyediakan sesi database untuk setiap request API.
    Memastikan koneksi ditutup setelah request selesai.
    """
    db = sessionmaker_factory()
    try:
        yield db
    finally:
        db.close()
