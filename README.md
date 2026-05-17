# SeaTrack 🌊

**SeaTrack** adalah sistem pendeteksi sampah perairan open-source yang dirancang untuk mendukung upaya pembersihan laut dan sungai secara otomatis. Menggunakan teknologi robotika terkini dan kecerdasan buatan, SeaTrack memungkinkan identifikasi sampah secara real-time melalui platform AUV (Autonomous Underwater Vehicle) atau ROV (Remotely Operated Vehicle).

## 🚀 Arsitektur Sistem

SeaTrack mengintegrasikan beberapa modul utama:

1.  **ROS 2 Node (Perception Layer):**
    *   Membaca feed kamera dari hardware robot.
    *   Mengolah stream video untuk deteksi.
2.  **ML Engine (Detection Layer):**
    *   Menjalankan model **YOLOv11** yang dioptimalkan dengan **OpenVINO**.
    *   Melakukan klasifikasi dan lokalisasi jenis sampah.
3.  **Telemetry Sender:**
    *   Mengirimkan koordinat deteksi dan metadata ke backend melalui protokol HTTP/Websocket.
4.  **Backend (Central Logic):**
    *   Dibangun dengan **FastAPI**.
    *   Menyimpan riwayat deteksi ke database **PostgreSQL**.
    *   Menyediakan API untuk dashboard monitoring.

## 📁 Struktur Folder

```text
SeaTrack/
├── ros2_ws/          # Workspace ROS 2 (Nodes & Interfaces)
│   └── src/
├── backend/          # API Service (FastAPI)
│   └── app/
├── ml_models/        # Model Weights & Inference Scripts
│   ├── weights/
│   └── scripts/
└── docs/             # Dokumentasi teknis tambahan
```

## 📅 Roadmap 1 Bulan (MVP Phase)

### Minggu 1: Fondasi & Setup Lingkungan
- [ ] Inisialisasi struktur proyek dan kontrol versi.
- [ ] Setup Docker environment untuk database PostgreSQL.
- [ ] Konfigurasi dasar workspace ROS 2 Humble/Foxy.
- [ ] Pembuatan skema database awal di FastAPI.

### Minggu 2: Ingesti Data & ML Baseline
- [ ] Implementasi ROS 2 node untuk pembacaan feed kamera (USB/RTSP).
- [ ] Integrasi model YOLOv11 standar ke dalam pipeline ROS 2.
- [ ] Uji coba inferensi awal menggunakan OpenCV/OpenVINO.

### Minggu 3: Integrasi Backend & Telemetri
- [ ] Pengembangan API Endpoint di FastAPI untuk menerima data deteksi.
- [ ] Implementasi node telemetri di ROS 2 untuk mengirim data ke Backend.
- [ ] Sinkronisasi data real-time antara robot dan server.

### Minggu 4: Optimasi & Dokumentasi
- [ ] Fine-tuning performa inferensi pada perangkat edge.
- [ ] Pembuatan dashboard sederhana untuk visualisasi hasil deteksi.
- [ ] Finalisasi dokumentasi API dan panduan deployment.

## 🤝 Kontribusi

Kami sangat terbuka untuk kontributor! Silakan buka *issue* atau kirimkan *pull request* untuk membantu membersihkan perairan kita.

---
