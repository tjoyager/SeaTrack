#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String  # Import tipe pesan String untuk data JSON
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import json  # Import library JSON untuk memformat data metadata

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        
        # Inisialisasi model YOLOv11 (versi nano untuk performa optimal di edge device)
        self.get_logger().info('Memuat model YOLOv11n...')
        self.model = YOLO('yolo11n.pt')
        
        # Inisialisasi CvBridge untuk konversi antara ROS 2 Image dan OpenCV
        self.bridge = CvBridge()
        
        # Subscriber untuk menerima data gambar dari topik kamera
        self.subscription = self.create_subscription(
            Image,
            '/seatrack/camera/image_raw',
            self.image_callback,
            10)
            
        # Publisher untuk mengirim gambar hasil deteksi (yang sudah ada bounding box)
        self.image_publisher = self.create_publisher(
            Image,
            '/seatrack/detection/image_annotated',
            10)
            
        # Publisher baru untuk mengirim metadata deteksi dalam format JSON
        # Topik: /seatrack/detection/data
        self.data_publisher = self.create_publisher(
            String,
            '/seatrack/detection/data',
            10)
            
        self.get_logger().info('YOLO Node siap mendeteksi objek!')

    def image_callback(self, msg):
        """
        Fungsi callback yang dipicu setiap kali pesan gambar baru masuk.
        """
        try:
            # 1. KONVERSI PESAN ROS 2 KE OPENCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # 2. INFERENSI YOLOv11
            results = self.model(cv_image, stream=True)
            
            # List untuk menampung metadata deteksi dari satu frame ini
            detections_metadata = []
            
            # 3. EKSTRAKSI DATA & ANOTASI
            for r in results:
                boxes = r.boxes
                
                for box in boxes:
                    # Ambil koordinat box
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ambil tingkat kepercayaan dan label
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    
                    # Simpan data deteksi ke dalam list metadata
                    # Format: {'class': nama_objek, 'confidence': skor_akurasi}
                    detections_metadata.append({
                        'class': label,
                        'confidence': round(conf, 2)
                    })
                    
                    # 4. MENGGAMBAR KE FRAME
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    display_text = f"{label} {conf:.2f}"
                    cv2.putText(cv_image, display_text, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 5. PUBLIKASI METADATA (JSON)
            # Mengubah list metadata menjadi string JSON
            json_msg = String()
            json_msg.data = json.dumps(detections_metadata)
            self.data_publisher.publish(json_msg)

            # 6. KONVERSI KEMBALI & PUBLIKASI GAMBAR
            annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            annotated_msg.header = msg.header
            self.image_publisher.publish(annotated_msg)

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
