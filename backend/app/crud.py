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
    
    Alur Logika:
    1. Menerima sesi database 'db'.
    2. Menggunakan query SQLAlchemy pada model 'Telemetry'.
    3. 'offset(skip)' digunakan untuk melewati sejumlah data (pagination).
    4. 'limit(limit)' membatasi jumlah data yang diambil agar tidak membebani memori.
    5. 'all()' mengeksekusi query dan mengembalikan list objek.
    """
    # Mengambil data dengan urutan terbaru di atas (opsional, bisa ditambah .order_by)
    return db.query(models.Telemetry).offset(skip).limit(limit).all()

def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate):
    """
    Fungsi untuk menyimpan data telemetri baru ke database.
    
    Alur Logika (Pydantic ke SQLAlchemy):
    1. Menerima data 'telemetry' yang sudah divalidasi oleh Pydantic (schemas.TelemetryCreate).
    2. Mengonversi Pydantic model menjadi SQLAlchemy model (models.Telemetry).
       '**telemetry.dict()' membongkar dictionary Pydantic menjadi argumen fungsi.
    3. 'db.add(db_telemetry)' mendaftarkan objek baru ke dalam sesi database.
    4. 'db.commit()' menyimpan perubahan secara permanen ke PostgreSQL.
    5. 'db.refresh(db_telemetry)' memperbarui objek lokal dengan data dari DB (seperti id dan timestamp).
    """
    # 1. Inisialisasi objek SQLAlchemy dengan data dari Pydantic
    db_telemetry = models.Telemetry(
        latitude=telemetry.latitude,
        longitude=telemetry.longitude,
        object_class=telemetry.object_class,
        confidence_score=telemetry.confidence_score
    )
    
    # 2. Tambahkan ke session
    db.add(db_telemetry)
    
    # 3. Simpan permanen ke database
    db.commit()
    
    # 4. Refresh agar mendapatkan ID dan timestamp otomatis
    db.refresh(db_telemetry)
    
    # 5. Kembalikan objek yang sudah berhasil disimpan
    return db_telemetry
