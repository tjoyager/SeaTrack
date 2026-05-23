from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles # Import untuk melayani file statis (HTML, CSS, JS)
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

# 3. Konfigurasi Static Files
# Mount folder 'static' agar bisa diakses via browser.
# Misalnya: file 'index.html' di 'app/static/' akan bisa diakses di 'http://localhost:8000/static/index.html'
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 4. Root Endpoint
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
    Endpoint POST untuk Menerima Data Deteksi Baru.
    """
    return crud.create_telemetry(db=db, telemetry=telemetry)

@app.get("/telemetry/", response_model=List[schemas.TelemetryResponse])
def get_telemetries_endpoint(
    skip: int = Query(0, description="Jumlah data yang dilewati (pagination)"),
    limit: int = Query(10, description="Batas maksimal data yang diambil"),
    db: Session = Depends(get_db)
):
    """
    Endpoint GET untuk Mengambil Riwayat Deteksi.
    """
    telemetries = crud.get_telemetries(db, skip=skip, limit=limit)
    return telemetries

# 5. System Health Endpoints

@app.post("/system-health/", response_model=schemas.SystemHealthResponse, status_code=201)
def create_system_health_endpoint(
    health: schemas.SystemHealthCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk menerima data kesehatan sistem dari ROS 2.
    """
    return crud.create_system_health(db=db, health=health)

@app.get("/system-health/latest", response_model=schemas.SystemHealthResponse)
def get_latest_health_endpoint(db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil status kesehatan sistem terbaru untuk dashboard.
    """
    health = crud.get_latest_system_health(db)
    if health is None:
        raise HTTPException(status_code=404, detail="No health data found")
    return health

# 6. Database Health Check (Opsional untuk Debugging)

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
