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
    """
    pass

class TelemetryResponse(TelemetryBase):
    """
    TelemetryResponse
    -----------------
    Model ini digunakan untuk format response yang dikirimkan balik ke client.
    """
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemHealthBase(BaseModel):
    """
    Model dasar untuk data kesehatan sistem.
    """
    cpu_usage: float = Field(..., description="Persentase penggunaan CPU")
    ram_usage: float = Field(..., description="Persentase penggunaan RAM")

class SystemHealthCreate(SystemHealthBase):
    """
    Schema untuk membuat data kesehatan sistem baru.
    """
    pass

class SystemHealthResponse(SystemHealthBase):
    """
    Schema untuk mengirimkan data kesehatan sistem ke Frontend.
    """
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
