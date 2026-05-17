import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

"""
CAMERA NODE (PERCEPTION LAYER) - VERSI OPENCV & CVBRIDGE
-------------------------------------------------------
Node ini bertanggung jawab untuk:
1. Membaca stream video dari webcam atau file video (.mp4).
2. Mengonversi frame OpenCV (BGR) menjadi pesan Image ROS 2.
3. Mempublikasikan gambar ke topik /seatrack/camera/image_raw.
"""

class CameraNode(Node):
    def __init__(self):
        # Inisialisasi node dengan nama 'camera_node'
        super().__init__('camera_node')

        # 1. Deklarasi Parameter
        # 'video_source' bisa berupa index webcam (0, 1, dst) atau path file video.
        self.declare_parameter('video_source', '0')
        # 'fps' menentukan seberapa sering gambar dipublikasikan.
        self.declare_parameter('fps', 30.0)

        # Mengambil nilai parameter
        self.video_source_param = self.get_parameter('video_source').get_parameter_value().string_value
        self.fps = self.get_parameter('fps').get_parameter_value().double_value

        # 2. Inisialisasi OpenCV VideoCapture
        # Coba konversi ke int jika input adalah angka (untuk webcam index)
        try:
            source = int(self.video_source_param)
        except ValueError:
            source = self.video_source_param

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            self.get_logger().error(f'Gagal membuka sumber video: {self.video_source_param}')
            return

        # 3. Inisialisasi CvBridge
        # Bridge ini adalah "jembatan" antara OpenCV (NumPy) dan ROS 2 (sensor_msgs/Image)
        self.bridge = CvBridge()

        # 4. Inisialisasi Publisher
        # Mempublikasikan ke topik '/seatrack/camera/image_raw' dengan queue size 10
        self.publisher_ = self.create_publisher(Image, '/seatrack/camera/image_raw', 10)

        # 5. Timer Callback
        # Menghitung interval timer berdasarkan FPS (1.0 / FPS)
        timer_period = 1.0 / self.fps
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(f'Camera Node berjalan menggunakan sumber: {self.video_source_param} pada {self.fps} FPS')

    def timer_callback(self):
        """
        Fungsi yang dipanggil secara periodik untuk membaca dan mengirim gambar.
        """
        # 1. Baca frame dari kamera/video
        ret, frame = self.cap.read()

        # 2. Error handling & Video Looping
        if not ret:
            # Jika sumber video adalah file, kita lakukan reset ke frame awal (looping)
            if isinstance(self.video_source_param, str) and os.path.isfile(self.video_source_param):
                self.get_logger().info('Video habis, melakukan looping...')
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return
            else:
                self.get_logger().error('Gagal mengambil frame dari kamera.')
                return

        try:
            # 3. Konversi format OpenCV (BGR8) menjadi pesan Image ROS 2
            # cv2.read() menghasilkan NumPy array dalam format BGR.
            # cv_bridge.cv2_to_imgmsg akan mengubahnya menjadi sensor_msgs/Image.
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

            # Menambahkan timestamp saat ini agar data sinkron
            img_msg.header.stamp = self.get_clock().now().to_msg()
            img_msg.header.frame_id = "camera_link"

            # 4. Publikasikan pesan ke ROS 2
            self.publisher_.publish(img_msg)

        except Exception as e:
            self.get_logger().error(f'Gagal melakukan konversi gambar: {str(e)}')

    def __del__(self):
        """
        Destructor untuk memastikan resource kamera dilepaskan saat node dimatikan.
        """
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Mematikan Camera Node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

