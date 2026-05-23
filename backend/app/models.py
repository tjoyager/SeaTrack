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
    """
    __tablename__ = "telemetries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    object_class = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Telemetry(id={self.id}, class={self.object_class}, score={self.confidence_score})>"

class SystemHealth(Base):
    """
    Model SystemHealth
    ------------------
    Tabel ini menyimpan status kesehatan perangkat edge AUV (CPU dan RAM).
    """
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Persentase penggunaan CPU (0.0 - 100.0)
    cpu_usage = Column(Float, nullable=False)
    
    # Persentase penggunaan RAM (0.0 - 100.0)
    ram_usage = Column(Float, nullable=False)

    def __repr__(self):
        return f"<SystemHealth(id={self.id}, cpu={self.cpu_usage}%, ram={self.ram_usage}%)>"
