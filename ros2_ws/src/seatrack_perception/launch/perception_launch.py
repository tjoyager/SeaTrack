import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    Fungsi utama yang wajib ada di setiap ROS 2 launch file.
    Fungsi ini mengembalikan objek LaunchDescription yang berisi daftar proses (node)
    yang akan dijalankan secara paralel oleh sistem ROS 2.
    """
    
    # 1. NODE KAMERA
    # Bertugas membaca frame dari kamera dan mempublikasikannya ke /seatrack/camera/image_raw
    camera_node = Node(
        package='seatrack_perception',      # Nama package ROS 2
        executable='camera_node',           # Nama alias/executable yang didefinisikan di setup.py
        name='camera_node',                 # Nama node saat berjalan (muncul di ros2 node list)
        output='screen',                    # Cetak log output (info, error) langsung ke terminal
        emulate_tty=True                    # Membantu format warna log di terminal
    )

    # 2. NODE YOLO (DETECTION LAYER)
    # Bertugas membaca gambar dari kamera, melakukan inferensi AI,
    # dan mempublikasikan metadata JSON ke /seatrack/detection/data
    yolo_node = Node(
        package='seatrack_perception',
        executable='yolo_node',
        name='yolo_node',
        output='screen',
        emulate_tty=True
    )

    # 3. NODE TELEMETRI (BRIDGE KE BACKEND)
    # Bertugas membaca metadata deteksi dan mengirimkannya via HTTP POST ke FastAPI
    telemetry_node = Node(
        package='seatrack_perception',
        executable='telemetry_node',
        name='telemetry_node',
        output='screen',
        emulate_tty=True
    )

    # Menyatukan semua node ke dalam satu daftar deskripsi peluncuran.
    # ROS 2 akan mengeksekusi semua node ini secara paralel (bersamaan) 
    # dalam proses mandirinya masing-masing, bukan berjalan berurutan.
    # Ini sangat cocok sebagai template: jika nanti ada node GPS/IMU, 
    # Anda cukup menambahkannya ke daftar ini.
    return LaunchDescription([
        camera_node,
        yolo_node,
        telemetry_node
    ])
