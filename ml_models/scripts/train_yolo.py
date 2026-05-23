import os
from ultralytics import YOLO

def train_custom_yolo():
    """
    Script Pelatihan Custom YOLOv11 - Project SeaTrack
    -------------------------------------------------
    Fungsi ini digunakan untuk melakukan fine-tuning model YOLOv11
    agar mampu mengenali jenis-jenis sampah laut yang spesifik.
    """

    # 1. Menentukan Path
    # Mendapatkan path absolut ke direktori script ini berada
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path ke file konfigurasi data.yaml hasil download Roboflow
    data_yaml_path = os.path.join(script_dir, "..", "dataset", "data.yaml")
    
    # Path ke model dasar (kita gunakan versi nano untuk efisiensi di robot)
    # Mencari di root workspace (sesuai struktur yang ada di session context)
    model_base_path = os.path.join(script_dir, "..", "..", "ros2_ws", "yolo11n.pt")
    
    # Path output untuk menyimpan hasil training (weights terbaik)
    output_weights_dir = os.path.join(script_dir, "..", "weights")

    # Pastikan folder weights tersedia
    os.makedirs(output_weights_dir, exist_ok=True)

    # 2. Inisialisasi Model
    # Load model YOLOv11 yang sudah dilatih sebelumnya (pre-trained) sebagai dasar transfer learning
    model = YOLO(model_base_path)

    # 3. Proses Pelatihan (Training)
    # Di sini kita memanggil fungsi .train() dengan parameter yang bisa di-tweak
    print("--- Memulai Pelatihan Model SeaTrack ---")
    
    results = model.train(
        data=data_yaml_path,      # Lokasi file data.yaml (konfigurasi dataset)
        epochs=5,                # Jumlah putaran pelatihan (1 epoch = seluruh dataset diproses sekali)
        imgsz=640,                # Ukuran resolusi gambar input (640x640 adalah standar YOLO)
        batch=16,                 # Jumlah gambar yang diproses bersamaan (sesuaikan dengan VRAM GPU)
        device='0',             # Gunakan '0' untuk GPU pertama, atau 'cpu' jika tidak ada GPU
        
        # Hyperparameters & Tuning
        patience=10,              # Berhenti otomatis jika akurasi tidak naik dalam 10 epoch (early stopping)
        optimizer='auto',         # Memilih optimizer terbaik secara otomatis (SGD, Adam, dll)
        lr0=0.01,                 # Learning rate awal (kecepatan belajar model)
        augment=True,             # Mengaktifkan augmentasi data otomatis (rotasi, flip, dll) untuk cegah overfitting
        
        # Output Logging
        project='SeaTrack_Train', # Nama project training
        name='debris_detector',   # Nama eksperimen spesifik ini
        exist_ok=True,            # Menimpa folder jika eksperimen dengan nama yang sama sudah ada
    )

    # 4. Menyimpan Hasil Terbaik
    # Secara default, YOLO menyimpan di 'runs/detect/debris_detector/weights/best.pt'
    # Kita akan menyalin atau memindahkan hasil terbaik ke folder ml_models/weights/ yang kita tentukan
    best_model_path = os.path.join(results.save_dir, 'weights', 'best.pt')
    target_path = os.path.join(output_weights_dir, 'yolo11n_seatrack_best.pt')
    
    if os.path.exists(best_model_path):
        import shutil
        shutil.copy(best_model_path, target_path)
        print(f"--- Training Selesai! Model terbaik disimpan di: {target_path} ---")
    else:
        print("Peringatan: File best.pt tidak ditemukan di direktori hasil training.")

if __name__ == "__main__":
    # Menjalankan fungsi training
    train_custom_yolo()
