from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

"""
MODELS MODULE
-------------
Modul ini mendefinisikan struktur tabel database menggunakan SQLAlchemy ORM.
Setiap class di sini merepresentasikan satu tabel di PostgreSQL.
"""

class Telemetry(Base):
    """
    Model Telemetry
    ---------------
    Tabel ini menyimpan data deteksi sampah yang dikirimkan dari node ROS 2.
    
    Atribut:
    - id: Primary key unik untuk setiap data masuk.
    - timestamp: Waktu saat objek terdeteksi (default: waktu saat data disimpan ke DB).
    - latitude: Koordinat lintang lokasi deteksi.
    - longitude: Koordinat bujur lokasi deteksi.
    - object_class: Label jenis sampah yang terdeteksi oleh YOLOv11 (contoh: 'plastic', 'bottle').
    - confidence_score: Tingkat kepercayaan deteksi model (0.0 sampai 1.0).
    """
    __tablename__ = "telemetries"

    # Kolom ID dengan auto-increment sebagai primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Timestamp otomatis menggunakan waktu server database saat entry dibuat
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Koordinat geografis menggunakan tipe Float
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Nama kelas objek (hasil klasifikasi YOLO)
    object_class = Column(String, nullable=False)
    
    # Skor kepercayaan deteksi
    confidence_score = Column(Float, nullable=False)

    def __repr__(self):
        """
        String representation untuk debugging
        """
        return f"<Telemetry(id={self.id}, class={self.object_class}, score={self.confidence_score})>"
