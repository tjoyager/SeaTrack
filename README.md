# SeaTrack 🌊

**SeaTrack** adalah sistem pendeteksi sampah perairan open-source yang dirancang untuk mendukung upaya pembersihan laut dan sungai secara otomatis. Menggunakan teknologi robotika terkini dan kecerdasan buatan, SeaTrack memungkinkan identifikasi sampah secara real-time melalui platform AUV (Autonomous Underwater Vehicle) atau ROV (Remotely Operated Vehicle).

## 🚀 Arsitektur Sistem

SeaTrack mengintegrasikan beberapa modul utama:

1.  **ROS 2 Node (Perception Layer):**
    *   `camera_node`: Membaca feed kamera dari hardware robot.
    *   `yolo_node`: Menjalankan inferensi model **YOLOv11** secara real-time.
    *   `telemetry_node`: Jembatan (bridge) data antara ROS 2 dan Backend FastAPI.
2.  **ML Engine (Detection Layer):**
    *   Menjalankan model **YOLOv11** (v11n.pt) untuk klasifikasi dan lokalisasi jenis sampah.
3.  **Backend (Central Logic):**
    *   Dibangun dengan **FastAPI**.
    *   Menyimpan riwayat deteksi ke database **SQLite**.
    *   Menyediakan API untuk dashboard monitoring.

## 📁 Struktur Folder

```text
SeaTrack/
├── ros2_ws/          # Workspace ROS 2 (Humble)
│   └── src/
│       └── seatrack_perception/
│           ├── launch/                 # ROS 2 Launch files
│           ├── seatrack_perception/    # Source code node (Python)
│           └── ...
├── backend/          # API Service (FastAPI)
│   ├── app/          # Source code aplikasi (CRUD, Models, Schemas)
│   └── seatrack.db   # Database SQLite
├── ml_models/        # Model Weights & Inference Scripts
└── README.md
```

## 🛠️ Cara Menjalankan Sistem

### 1. Jalankan Backend (FastAPI)
Buka terminal baru:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Jalankan Sistem Persepsi (ROS 2)
Buka terminal baru:
```bash
cd ros2_ws
source install/setup.bash
ros2 launch seatrack_perception perception_launch.py
```

## 📅 Progress & Roadmap (MVP Phase)

### Minggu 1-2: Fondasi & Setup Lingkungan
- [x] Inisialisasi struktur proyek dan workspace ROS 2.
- [x] Setup database lokal menggunakan SQLite dan skema Pydantic.
- [x] Implementasi `camera_node` untuk pembacaan feed kamera (USB/OpenCV).

### Minggu 3: Deteksi AI & Integrasi Backend (Current)
- [x] Integrasi model **YOLOv11n** ke dalam pipeline ROS 2 (`yolo_node`).
- [x] Ekstraksi metadata deteksi (JSON) dan anotasi visual secara real-time.
- [x] Implementasi `telemetry_node` dengan fitur **Throttling/Rate Limiting** (2 detik) untuk efisiensi backend.
- [x] Penanganan error sinkronisasi skema data (Fix 422 Unprocessable Entity).
- [x] Pembuatan **ROS 2 Launch File** untuk orkestrasi node secara paralel.

### Minggu 4: Optimasi & Visualisasi
- [ ] Pengujian lapangan dengan data sampah sungai asli.
- [ ] Fine-tuning performa inferensi pada perangkat edge.
- [ ] Pembuatan dashboard sederhana untuk visualisasi hasil deteksi.

## 🤝 Kontribusi

Kami sangat terbuka untuk kontributor! Silakan buka *issue* atau kirimkan *pull request* untuk membantu membersihkan perairan kita.

---
*Last Updated: Hari ke-9 - Integrasi End-to-End Berhasil.*
