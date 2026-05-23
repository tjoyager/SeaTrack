import os
from ultralytics import YOLO

def export_to_openvino():
    """
    Script Konversi YOLOv11 ke OpenVINO - Project SeaTrack
    -----------------------------------------------------
    Script ini mengoptimalkan model .pt hasil training agar dapat berjalan
    jauh lebih cepat di CPU perangkat edge (seperti Intel NUC atau laptop)
    menggunakan toolkit OpenVINO.
    """

    # 1. Menentukan Path Model
    # Mendapatkan path absolut ke direktori script ini berada
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path ke file weights hasil training Colab sebelumnya
    model_path = os.path.join(script_dir, "..", "weights", "yolo11n_seatrack_best.pt")
    
    # Validasi keberadaan file model
    if not os.path.exists(model_path):
        print(f"Error: File model tidak ditemukan di {model_path}")
        return

    # 2. Inisialisasi Model Ultralytics
    print(f"--- Memuat model untuk konversi: {model_path} ---")
    model = YOLO(model_path)

    # 3. Proses Export ke OpenVINO
    # Parameter 'format' diisi 'openvino' untuk menghasilkan folder .xml dan .bin
    # Perangkat edge biasanya menggunakan presisi FP16 untuk keseimbangan speed & akurasi
    print("--- Memulai proses optimasi OpenVINO (ini mungkin butuh waktu beberapa menit) ---")
    
    export_path = model.export(
        format='openvino',   # Format target
        imgsz=640,           # Resolusi gambar (harus sama dengan saat training)
        half=True,           # Menggunakan presisi FP16 (lebih cepat di CPU Intel)
        int8=False           # Ubah ke True jika ingin kuantisasi lebih ekstrim (tapi akurasi turun)
    )

    print(f"--- Konversi Selesai! Model OpenVINO disimpan di: {export_path} ---")
    print("Catatan: Folder tersebut berisi file .xml dan .bin yang dibutuhkan OpenVINO.")

if __name__ == "__main__":
    export_to_openvino()
