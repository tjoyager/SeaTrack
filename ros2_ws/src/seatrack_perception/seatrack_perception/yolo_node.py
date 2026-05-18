#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        
        # Inisialisasi model YOLOv11 (versi nano untuk performa optimal di edge device)
        # Model yolo11n.pt akan otomatis diunduh saat pertama kali dijalankan
        self.get_logger().info('Memuat model YOLOv11n...')
        self.model = YOLO('yolo11n.pt')
        
        # Inisialisasi CvBridge untuk konversi antara ROS 2 Image dan OpenCV
        self.bridge = CvBridge()
        
        # Subscriber untuk menerima data gambar dari topik kamera
        # Topik: /seatrack/camera/image_raw
        self.subscription = self.create_subscription(
            Image,
            '/seatrack/camera/image_raw',
            self.image_callback,
            10)
            
        # Publisher untuk mengirim gambar hasil deteksi (yang sudah ada bounding box)
        # Topik: /seatrack/detection/image_annotated
        self.publisher_ = self.create_publisher(
            Image,
            '/seatrack/detection/image_annotated',
            10)
            
        self.get_logger().info('YOLO Node siap mendeteksi objek!')

    def image_callback(self, msg):
        """
        Fungsi callback yang dipicu setiap kali pesan gambar baru masuk.
        """
        try:
            # 1. KONVERSI PESAN ROS 2 KE OPENCV
            # Menggunakan CvBridge untuk mengubah sensor_msgs/Image menjadi numpy array (BGR8)
            # 'bgr8' adalah format standar OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # 2. INFERENSI YOLOv11
            # Menjalankan deteksi objek pada frame yang diterima
            # stream=True memberikan generator objek yang lebih hemat memori
            results = self.model(cv_image, stream=True)
            
            # 3. EKSTRAKSI DATA & ANOTASI
            # Kita melakukan iterasi pada hasil deteksi (results)
            for r in results:
                # Ambil data box (bounding box) dari hasil deteksi
                boxes = r.boxes
                
                for box in boxes:
                    # Ambil koordinat box [x1, y1, x2, y2]
                    # .xyxy[0] mengambil koordinat dalam format pixel absolut
                    x1, y1, x2, y2 = box.xyxy[0]
                    # Konversi dari tensor ke integer agar bisa digambar oleh OpenCV
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ambil tingkat kepercayaan (confidence score)
                    conf = float(box.conf[0])
                    
                    # Ambil indeks kelas dan cari nama kelasnya (misal: 'person', 'boat', dll)
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    
                    # 4. MENGGAMBAR KE FRAME
                    # Gambar kotak (bounding box) berwarna hijau (0, 255, 0) dengan ketebalan 2
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Siapkan teks label (Nama: Persentase)
                    display_text = f"{label} {conf:.2f}"
                    
                    # Gambar latar belakang teks agar mudah dibaca
                    cv2.putText(cv_image, display_text, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 5. KONVERSI KEMBALI KE PESAN ROS 2
            # Mengubah numpy array (OpenCV) yang sudah dianotasi kembali menjadi sensor_msgs/Image
            annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            
            # Pastikan timestamp pesan sama dengan pesan input agar sinkronisasi terjaga
            annotated_msg.header = msg.header
            
            # 6. PUBLIKASI
            # Kirim gambar ke topik /seatrack/detection/image_annotated
            self.publisher_.publish(annotated_msg)

        except Exception as e:
            self.get_logger().error(f'Gagal memproses gambar: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    yolo_node = YoloNode()
    try:
        rclpy.spin(yolo_node)
    except KeyboardInterrupt:
        pass
    finally:
        yolo_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
