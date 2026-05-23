import os
from roboflow import Roboflow

def download_data():
    # 1. Inisialisasi Roboflow dengan API Key yang Anda berikan
    rf = Roboflow(api_key="s993w2Fuazt7L9LRYk1m")
    
    # 2. Akses Project
    project = rf.workspace("aryan-fqdxw").project("trash-detection-in-water-hp6yd")
    version = project.version(1)
    
    # 3. Tentukan lokasi download agar rapi di ml_models/dataset
    # os.getcwd() akan mengambil root dari workspace SeaTrack
    dataset_path = os.path.join(os.getcwd(), "ml_models", "dataset")
    
    # Hapus folder dataset lama jika ada agar tidak bentrok
    if os.path.exists(dataset_path):
        import shutil
        print(f"Membersihkan folder lama di {dataset_path}...")
        shutil.rmtree(dataset_path)

    # 4. Download dataset dalam format YOLOv11
    print(f"Sedang mengunduh dataset 'trash-detection-in-water' ke {dataset_path}...")
    dataset = version.download("yolov11", location=dataset_path)
    
    print("\n--- Download Selesai! ---")
    print(f"Lokasi data.yaml baru: {os.path.join(dataset_path, 'data.yaml')}")

if __name__ == "__main__":
    download_data()
