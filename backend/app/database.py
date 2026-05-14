from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""
DATABASE MODULE
---------------
Modul ini bertanggung jawab untuk mengatur koneksi antara aplikasi FastAPI 
dan database PostgreSQL menggunakan SQLAlchemy ORM.
"""

# 1. Database URL
# Format: postgresql://[user]:[password]@[host]:[port]/[db_name]
# TODO: Pindahkan kredensial ini ke file .env demi keamanan produksi
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password_anda@localhost:5432/seatrack_db"

# 2. Engine Creation
# Engine adalah titik masuk utama untuk koneksi database.
# 'create_engine' akan mengelola pool koneksi ke PostgreSQL.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# 3. Session Configuration
# SessionLocal adalah class yang akan kita instansiasi untuk setiap request database.
# autocommit=False: Perubahan tidak langsung disimpan sampai kita memanggil session.commit()
# autoflush=False: Mencegah SQL dikirim ke DB secara otomatis sebelum commit
sessionmaker_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Class
# Base adalah class dasar yang akan diwarisi oleh semua model database kita (di models.py).
# SQLAlchemy menggunakan ini untuk memetakan class Python ke tabel database.
Base = declarative_base()

def get_db():
    """
    Dependency Generator
    --------------------
    Fungsi ini akan digunakan sebagai 'Dependency' di FastAPI.
    Fungsi ini membuka sesi database saat request masuk dan 
    memastikan sesi ditutup setelah request selesai, baik sukses maupun error.
    """
    db = sessionmaker_factory()
    try:
        yield db
    finally:
        # Menutup koneksi untuk mencegah kebocoran resource
        db.close()
