from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from . import models, schemas, crud

"""
MAIN APPLICATION MODULE
-----------------------
Titik masuk (entry point) utama untuk aplikasi SeaTrack Backend.
Di sini kita menginisialisasi FastAPI, menghubungkan router, 
dan mengatur logika startup aplikasi.
"""

# 1. Database Synchronization
# Membuat tabel di database jika belum ada.
models.Base.metadata.create_all(bind=engine)

# 2. FastAPI Instance
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

# 4. Telemetry Endpoints

@app.post("/telemetry/", response_model=schemas.TelemetryResponse, status_code=201)
def create_telemetry_endpoint(
    telemetry: schemas.TelemetryCreate, 
    db: Session = Depends(get_db)
):
    """
    Endpoint POST untuk Menerima Data Deteksi Baru
    ---------------------------------------------
    Endpoint ini akan dipanggil oleh robot (node ROS 2) setiap kali ada sampah terdeteksi.
    
    Alur Logika:
    1. FastAPI menerima JSON request body.
    2. Pydantic (schemas.TelemetryCreate) memvalidasi tipe data & struktur JSON.
    3. Jika valid, 'telemetry' diteruskan ke fungsi 'crud.create_telemetry'.
    4. Data disimpan ke PostgreSQL melalui SQLAlchemy.
    5. Mengembalikan objek telemetry lengkap dengan ID dan Timestamp (schemas.TelemetryResponse).
    """
    # Memanggil fungsi CRUD untuk menyimpan data ke database
    return crud.create_telemetry(db=db, telemetry=telemetry)

@app.get("/telemetry/", response_model=List[schemas.TelemetryResponse])
def get_telemetries_endpoint(
    skip: int = Query(0, description="Jumlah data yang dilewati (pagination)"),
    limit: int = Query(10, description="Batas maksimal data yang diambil"),
    db: Session = Depends(get_db)
):
    """
    Endpoint GET untuk Mengambil Riwayat Deteksi
    --------------------------------------------
    Endpoint ini digunakan oleh Frontend atau aplikasi Monitoring untuk melihat data deteksi.
    
    Alur Logika:
    1. Menerima query parameter 'skip' dan 'limit' untuk fitur pagination.
    2. Memanggil 'crud.get_telemetries' untuk menarik data dari database.
    3. Mengembalikan list objek telemetry dalam format yang sesuai dengan 'TelemetryResponse'.
    """
    # Mengambil data dari database menggunakan fungsi CRUD
    telemetries = crud.get_telemetries(db, skip=skip, limit=limit)
    return telemetries

# 5. Database Health Check (Opsional untuk Debugging)
@app.get("/health-db")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Memverifikasi koneksi ke database PostgreSQL.
    """
    try:
        # Melakukan test query sederhana
        db.execute(models.Base.metadata.tables['telemetries'].select())
        return {"status": "success", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Instruksi Jalankan:
# uvicorn app.main:app --reload
