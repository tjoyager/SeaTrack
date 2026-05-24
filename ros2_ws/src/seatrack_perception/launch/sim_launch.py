from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    Fungsi utama peluncuran untuk lingkungan simulasi Gazebo.
    Di sini kita tidak menjalankan camera_node karena aliran gambar
    sudah disediakan langsung oleh plugin kamera dari lingkungan simulasi Gazebo.
    """
    
    # NODE YOLO (DETECTION LAYER)
    # Bertugas membaca gambar dari kamera, melakukan inferensi AI,
    # dan mempublikasikan metadata JSON.
    yolo_node = Node(
        package='seatrack_perception',
        executable='yolo_node',
        name='yolo_node',
        output='screen',
        emulate_tty=True,
        # ---------------------------------------------------------------------
        # KONSEP PARAMETER DAN REMAPPING TOPIK DI ROS 2:
        # ROS 2 memungkinkan kita untuk mengubah perilaku dari sebuah node saat 
        # diluncurkan (runtime) tanpa perlu mengubah kode sumber (.py) nya sama sekali.
        #
        # Pada file 'yolo_node.py', kita telah mendeklarasikan parameter 'image_topic' 
        # dengan nilai default '/seatrack/camera/image_raw' (digunakan untuk kamera fisik).
        #
        # Dengan menyisipkan kamus (dictionary) 'parameters' di bawah ini saat meluncurkan
        # node tersebut, kita "menimpa" (override) nilai default tersebut. 
        # Di sini, kita mengubah topiknya menjadi '/camera/image_raw', yaitu topik standar 
        # keluaran dari plugin kamera simulasi Gazebo. 
        #
        # Fleksibilitas inilah inti dari ROS 2: Node YOLO yang sama persis dapat dipakai 
        # di AUV fisik sesungguhnya dan juga di simulasi Gazebo hanya dengan mengubah 
        # Launch File-nya.
        # ---------------------------------------------------------------------
        parameters=[
            {'image_topic': '/camera/image_raw'}
        ]
    )

    # NODE TELEMETRI (BRIDGE KE BACKEND)
    # Bertugas membaca metadata deteksi dan mengirimkannya via HTTP POST ke FastAPI
    telemetry_node = Node(
        package='seatrack_perception',
        executable='telemetry_node',
        name='telemetry_node',
        output='screen',
        emulate_tty=True
    )

    # Mengembalikan LaunchDescription hanya dengan yolo_node dan telemetry_node
    # Sistem siap untuk mendengarkan gambar yang dikirim oleh Gazebo.
    return LaunchDescription([
        yolo_node,
        telemetry_node
    ])
