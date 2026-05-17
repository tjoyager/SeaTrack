import rclpy
from rclpy.node import Node

"""
CAMERA NODE (PERCEPTION LAYER)
------------------------------
Node ini bertanggung jawab untuk menangkap feed video dari kamera dan 
menyiapkannya untuk diproses oleh model AI (YOLO). 
Pada tahap awal, node ini hanya berfungsi sebagai boilerplate dasar.
"""

class CameraNode(Node):
    """
    Class CameraNode
    ----------------
    Mewarisi dari rclpy.node.Node untuk menjadi node ROS 2 yang sah.
    """
    def __init__(self):
        # Inisialisasi node dengan nama 'camera_node'
        super().__init__('camera_node')
        
        # Mencetak log info saat node berhasil dijalankan
        self.get_logger().info('Camera node initialized and waiting for feed...')
        
        # Membuat timer yang akan menjalankan fungsi callback setiap 1 detik
        # (Simulasi capture frame/proses berkala)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        """
        Timer Callback
        --------------
        Fungsi ini dijalankan secara periodik berdasarkan timer yang dibuat.
        Untuk saat ini hanya mencetak status node.
        """
        self.get_logger().info('Camera node is active...')

def main(args=None):
    """
    Entry Point
    -----------
    Titik masuk utama untuk menjalankan node.
    """
    # 1. Inisialisasi sistem komunikasi ROS 2
    rclpy.init(args=args)
    
    # 2. Instansiasi class CameraNode
    node = CameraNode()
    
    try:
        # 3. Spin node agar tetap berjalan dan merespon callback/timer
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Menangani penghentian paksa dengan CTRL+C
        node.get_logger().info('Camera node stopping...')
    finally:
        # 4. Cleanup: Hancurkan node dan shutdown ROS 2
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
