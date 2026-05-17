from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

"""
SCHEMAS MODULE
--------------
Modul ini mendefinisikan Pydantic models yang digunakan untuk validasi data.
Pydantic memastikan data yang masuk dari API atau keluar dari API memiliki tipe data yang benar.
"""

class TelemetryBase(BaseModel):
    """
    TelemetryBase
    -------------
    Model dasar yang berisi kolom-kolom umum yang digunakan baik untuk
    membuat data baru (Create) maupun untuk mengirim response (Read).
    """
    # Koordinat lintang lokasi robot
    latitude: float = Field(..., description="Koordinat lintang (latitude) lokasi deteksi")
    
    # Koordinat bujur lokasi robot
    longitude: float = Field(..., description="Koordinat bujur (longitude) lokasi deteksi")
    
    # Label kelas objek (contoh: plastic, metal, wood)
    object_class: str = Field(..., description="Jenis sampah yang terdeteksi")
    
    # Skor kepercayaan dari model AI (0.0 - 1.0)
    confidence_score: float = Field(..., description="Tingkat kepercayaan deteksi (0.0 - 1.0)")

class TelemetryCreate(TelemetryBase):
    """
    TelemetryCreate
    ---------------
    Model ini digunakan khusus untuk data yang datang dari ROS 2 ke API.
    Model ini mewarisi semua field dari TelemetryBase.
    """
    # Saat ini tidak ada tambahan field khusus untuk create,
    # namun class ini dibuat agar struktur kode tetap bersih jika nanti ada field khusus input.
    pass

class TelemetryResponse(TelemetryBase):
    """
    TelemetryResponse
    -----------------
    Model ini digunakan untuk format response yang dikirimkan balik ke client (Frontend/Mobile).
    Menambahkan field 'id' dan 'timestamp' yang dihasilkan secara otomatis oleh database.
    """
    # ID unik dari database
    id: int
    
    # Waktu otomatis saat data masuk
    timestamp: datetime

    class Config:
        """
        Konfigurasi Pydantic untuk mendukung SQLAlchemy ORM.
        Ini memungkinkan Pydantic untuk membaca data langsung dari objek SQLAlchemy
        (misal: data.id bukannya data['id']).
        """
        from_attributes = True
