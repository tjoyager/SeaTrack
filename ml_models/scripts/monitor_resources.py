import psutil
import time
import os

def monitor_cpu_usage(interval=1.0):
    """
    Script Monitoring Penggunaan CPU - Project SeaTrack
    --------------------------------------------------
    Gunakan script ini untuk membandingkan penggunaan CPU sebelum dan 
    sesudah menggunakan OpenVINO. 
    
    Target: Penggunaan CPU harus lebih stabil dan efisiensi per frame meningkat.
    """
    print("--- Memulai Monitoring CPU SeaTrack AUV ---")
    print("Tekan Ctrl+C untuk menghentikan.")
    print("-" * 40)
    
    try:
        while True:
            # Mengambil persentase penggunaan CPU per core
            cpu_percent_total = psutil.cpu_percent(interval=interval)
            cpu_per_core = psutil.cpu_percent(percpu=True)
            
            # Mengambil info memori (RAM)
            memory = psutil.virtual_memory()
            
            # Membersihkan terminal (opsional, agar tampilan rapi)
            # os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"Total CPU Usage: {cpu_percent_total}%")
            print(f"RAM Usage: {memory.percent}% ({memory.used / (1024**2):.1f}MB / {memory.total / (1024**2):.1f}MB)")
            
            # Menampilkan beban per core (penting untuk melihat load balancing OpenVINO)
            core_str = " | ".join([f"C{i}: {p}%" for i, p in enumerate(cpu_per_core)])
            print(f"Per Core: {core_str}")
            print("-" * 40)
            
    except KeyboardInterrupt:
        print("\nMonitoring dihentikan.")

if __name__ == "__main__":
    # Pastikan library psutil terinstall
    # Jika belum: pip install psutil
    monitor_cpu_usage()
