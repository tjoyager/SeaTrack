from sqlalchemy.orm import Session
from . import models, schemas

"""
CRUD MODULE (Create, Read, Update, Delete)
------------------------------------------
Modul ini berisi logika bisnis utama untuk berinteraksi dengan database.
Kita memisahkan logika ini dari router API agar kode lebih bersih dan mudah diuji.
"""

def get_telemetries(db: Session, skip: int = 0, limit: int = 100):
    """
    Fungsi untuk mengambil daftar data telemetri dari database.
    """
    return db.query(models.Telemetry).order_by(models.Telemetry.timestamp.desc()).offset(skip).limit(limit).all()

def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate):
    """
    Fungsi untuk menyimpan data telemetri baru ke database.
    """
    db_telemetry = models.Telemetry(
        latitude=telemetry.latitude,
        longitude=telemetry.longitude,
        object_class=telemetry.object_class,
        confidence_score=telemetry.confidence_score
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

def create_system_health(db: Session, health: schemas.SystemHealthCreate):
    """
    Menyimpan data kesehatan sistem (CPU/RAM) ke database.
    """
    db_health = models.SystemHealth(
        cpu_usage=health.cpu_usage,
        ram_usage=health.ram_usage
    )
    db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health

def get_latest_system_health(db: Session):
    """
    Mengambil data kesehatan sistem terbaru.
    """
    return db.query(models.SystemHealth).order_by(models.SystemHealth.timestamp.desc()).first()
