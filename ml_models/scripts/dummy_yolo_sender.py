import requests
import random
import time
import json
from datetime import datetime

"""
DUMMY YOLO SENDER SCRIPT
------------------------
Skrip ini mensimulasikan pengiriman data hasil deteksi dari model YOLO (AI) 
ke backend FastAPI. Digunakan untuk pengujian integrasi sebelum sistem 
robotik (ROS 2) dan model AI sungguhan dihubungkan.
"""

# Konfigurasi Endpoint API
# Alamat server backend SeaTrack yang berjalan di localhost
API_URL = "http://127.0.0.1:8000/telemetry/"

# Daftar jenis sampah dummy yang akan dideteksi oleh AI
WASTE_TYPES = ["plastic bottle", "fishing net", "tire", "plastic bag", "metal can"]

def generate_dummy_data():
    """
    Fungsi untuk menghasilkan data deteksi acak.
    Mensimulasikan output dari model YOLOv11.
    """
    # Memilih jenis sampah secara acak dari daftar
    object_class = random.choice(WASTE_TYPES)
    
    # Menghasilkan skor kepercayaan (confidence) acak antara 0.70 - 0.99
    confidence_score = round(random.uniform(0.70, 0.99), 2)
    
    # Menghasilkan koordinat latitude acak di sekitar wilayah perairan dummy
    # Rentang ini hanya contoh (sekitar Jakarta/Laut Jawa)
    latitude = round(random.uniform(-6.20, -6.10), 6)
    
    # Menghasilkan koordinat longitude acak
    longitude = round(random.uniform(106.70, 106.90), 6)
    
    return {
        "object_class": object_class,
        "confidence_score": confidence_score,
        "latitude": latitude,
        "longitude": longitude
    }

def send_telemetry():
    """
    Fungsi utama untuk mengirimkan data ke backend secara terus-menerus.
    """
    print("--- Simulasi YOLO Telemetry Sender Dimulai ---")
    print(f"Mengirim data ke: {API_URL}")
    print("Tekan CTRL+C untuk menghentikan simulasi.\n")

    try:
        while True:
            # 1. Siapkan data deteksi dummy
            payload = generate_dummy_data()
            
            # 2. Kirim data menggunakan metode HTTP POST
            try:
                # Mengirim request JSON ke backend
                response = requests.post(API_URL, json=payload, timeout=5)
                
                # 3. Cek status respon dari server
                if response.status_code == 201:
                    # Data berhasil disimpan (Created)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] BERHASIL: Mengirim {payload['object_class']} "
                          f"(Conf: {payload['confidence_score']}) ke server.")
                else:
                    # Terjadi error pada server atau validasi data
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] GAGAL: Server merespon dengan status {response.status_code}")
                    print(f"Detail Error: {response.text}")
            
            except requests.exceptions.ConnectionError:
                # Backend mungkin belum dijalankan
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: Tidak dapat terhubung ke backend. "
                      "Pastikan uvicorn sudah berjalan!")
            
            # 4. Tunggu selama 5 detik sebelum mengirim data berikutnya
            time.sleep(5)

    except KeyboardInterrupt:
        # Menangani saat user menekan CTRL+C
        print("\nSimulasi dihentikan oleh pengguna.")

if __name__ == "__main__":
    # Jalankan fungsi utama
    send_telemetry()
