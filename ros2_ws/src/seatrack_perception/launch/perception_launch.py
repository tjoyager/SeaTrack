import os
from datetime import datetime
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def evaluate_record_bag(context, *args, **kwargs):
    """
    Fungsi ini dipanggil oleh OpaqueFunction saat runtime.
    OpaqueFunction sangat berguna ketika kita perlu mengeksekusi logika Python biasa
    (seperti membuat direktori atau mengecek waktu saat ini) yang bergantung pada
    nilai dari parameter LaunchConfiguration yang baru diketahui saat file di-launch.
    """
    
    # 1. Mengambil nilai string dari argumen 'record_bag'
    record_bag_value = LaunchConfiguration('record_bag').perform(context)
    
    # Jika argumen bernilai 'true', siapkan proses perekaman ROS 2 Bag
    if record_bag_value.lower() == 'true':
        
        # 2. Penanganan Direktori Penyimpanan
        home_dir = os.path.expanduser('~')
        bags_dir = os.path.join(home_dir, 'Project', 'SeaTrack', 'ros2_ws', 'bags')
        
        # Membuat folder 'bags/' jika belum ada secara otomatis
        if not os.path.exists(bags_dir):
            os.makedirs(bags_dir)
            
        # 3. Penamaan File Dinamis dengan Timestamp
        # Menambahkan format waktu (TahunBulanTanggal_JamMenitDetik) 
        # untuk memastikan setiap rekaman misi memiliki nama file yang unik.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bag_name = f"mission_record_{timestamp}"
        output_path = os.path.join(bags_dir, bag_name)
        
        print(f"[INFO] ROS 2 Bag Recording diaktifkan. Menyimpan rekaman ke: {output_path}")
        
        # 4. Membuat Proses Tambahan (ExecuteProcess)
        # Menjalankan perintah bash setara dengan: 
        # ros2 bag record /seatrack/camera/image_raw /seatrack/detection/data /seatrack/detection/image_annotated -o <path>
        record_action = ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '/seatrack/camera/image_raw',
                '/seatrack/detection/data',
                '/seatrack/detection/image_annotated',
                '-o', output_path
            ],
            output='screen'
        )
        
        # Mengembalikan aksi tersebut agar dieksekusi oleh Launch System
        return [record_action]
        
    # Jika bernilai 'false', jangan kembalikan aksi apa pun (tidak merekam)
    return []


def generate_launch_description():
    """
    Fungsi utama yang mengembalikan LaunchDescription.
    """
    
    # -------------------------------------------------------------------------
    # DEKLARASI ARGUMEN LAUNCH
    # Kita mendeklarasikan argumen 'record_bag' sehingga pengguna bisa 
    # meluncurkan sistem dengan cara:
    # ros2 launch seatrack_perception perception_launch.py record_bag:=true
    # -------------------------------------------------------------------------
    record_bag_arg = DeclareLaunchArgument(
        'record_bag',
        default_value='false',
        description='Set ke "true" untuk merekam topik penting menggunakan ros2 bag'
    )
    
    # -------------------------------------------------------------------------
    # OPAQUE FUNCTION
    # OpaqueFunction "membungkus" fungsi evaluate_record_bag agar sistem Launch 
    # bisa melewatkan objek 'context' kepadanya, sehingga kita dapat 
    # mengekstrak nilai argumen saat runtime dan menyusun ExecuteProcess.
    # -------------------------------------------------------------------------
    bag_recording_action = OpaqueFunction(function=evaluate_record_bag)

    # 1. NODE KAMERA
    camera_node = Node(
        package='seatrack_perception',
        executable='camera_node',
        name='camera_node',
        output='screen',
        emulate_tty=True
    )

    # 2. NODE YOLO (DETECTION LAYER)
    yolo_node = Node(
        package='seatrack_perception',
        executable='yolo_node',
        name='yolo_node',
        output='screen',
        emulate_tty=True
    )

    # 3. NODE TELEMETRI (BRIDGE KE BACKEND)
    telemetry_node = Node(
        package='seatrack_perception',
        executable='telemetry_node',
        name='telemetry_node',
        output='screen',
        emulate_tty=True
    )

    # Menyusun semua aksi dan argumen ke dalam daftar LaunchDescription
    return LaunchDescription([
        record_bag_arg,
        bag_recording_action,
        camera_node,
        yolo_node,
        telemetry_node
    ])
