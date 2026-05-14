from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models

"""
MAIN APPLICATION MODULE
-----------------------
Titik masuk (entry point) utama untuk aplikasi SeaTrack Backend.
Di sini kita menginisialisasi FastAPI, menghubungkan router, 
dan mengatur logika startup aplikasi.
"""

# 1. Database Synchronization
# Baris ini memerintahkan SQLAlchemy untuk membuat semua tabel yang didefinisikan 
# di modul 'models' jika tabel tersebut belum ada di database.
# PERINGATAN: Di lingkungan produksi yang kompleks, disarankan menggunakan 
# alat migrasi seperti 'Alembic' daripada bind langsung seperti ini.
models.Base.metadata.create_all(bind=engine)

# 2. FastAPI Instance
# Inisialisasi aplikasi dengan metadata dasar
app = FastAPI(
    title="SeaTrack Backend API",
    description="Backend service untuk sistem pendeteksi sampah perairan SeaTrack.",
    version="0.1.0"
)

# 3. Root Endpoint
@app.get("/")
def read_root():
    """
    Health Check Endpoint
    ---------------------
    Digunakan untuk memverifikasi bahwa layanan backend berjalan dengan baik.
    """
    return {
        "status": "online",
        "message": "SeaTrack Backend is running",
        "version": "0.1.0"
    }

# 4. Example Telemetry Endpoint (Boilerplate)
@app.get("/health-db")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Database Connection Check
    -------------------------
    Endpoint sederhana untuk memverifikasi apakah koneksi ke PostgreSQL berhasil.
    Jika fungsi ini mengembalikan respons sukses, berarti konfigurasi database sudah benar.
    """
    try:
        # Melakukan query sederhana untuk memastikan koneksi aktif
        db.execute(models.Base.metadata.tables['telemetries'].select())
        return {"status": "success", "database": "connected"}
    except Exception as e:
        # Jika terjadi kesalahan koneksi, kirim error HTTP 500
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Instruksi Jalankan:
# Untuk menjalankan server pengembangan, gunakan perintah:
# uvicorn app.main:app --reload
