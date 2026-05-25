#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String  # Import tipe pesan String untuk data JSON
from cv_bridge import CvBridge
import cv2
import os
from ultralytics import YOLO
import json  # Import library JSON untuk memformat data metadata

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        
        # 1. Deklarasi Parameter Model
        # Prioritas sekarang diberikan ke folder hasil export OpenVINO
        home_dir = os.path.expanduser('~')
        default_openvino_path = os.path.join(home_dir, 'Project', 'SeaTrack', 'ml_models', 'weights', 'yolo11n_seatrack_best_openvino_model')
        default_pt_path = os.path.join(home_dir, 'Project', 'SeaTrack', 'ml_models', 'weights', 'yolo11n_seatrack_best.pt')
        
        self.declare_parameter('model_path', default_openvino_path)
        model_path = self.get_parameter('model_path').get_parameter_value().string_value
        
        # Deklarasi Parameter Topik Gambar untuk mendukung fleksibilitas antara Gazebo dan Kamera Fisik
        self.declare_parameter('image_topic', '/seatrack/camera/image_raw')
        image_topic = self.get_parameter('image_topic').get_parameter_value().string_value
        
        # 2. Inisialisasi model YOLOv11 dengan Pengecekan Format
        if os.path.exists(model_path):
            # Jika yang ditemukan adalah folder OpenVINO
            if 'openvino' in model_path.lower():
                self.get_logger().info('--- [OPTIMASI] Sistem berjalan menggunakan OpenVINO Inference Engine ---')
            else:
                self.get_logger().info(f'Memuat model kustom standar: {model_path}')
        elif os.path.exists(default_pt_path):
            # Fallback ke file .pt jika folder OpenVINO belum ada
            self.get_logger().warn(f'Model OpenVINO tidak ditemukan di {model_path}. Menggunakan file .pt kustom.')
            model_path = default_pt_path
        else:
            # Fallback terakhir ke model standar ultralytics
            self.get_logger().warn('Model kustom tidak ditemukan. Menggunakan model default yolo11n.pt')
            model_path = 'yolo11n.pt'
        
        self.get_logger().info(f'Path Model Aktif: {model_path}')
        self.model = YOLO(model_path, task='detect')
        
        # Inisialisasi CvBridge untuk konversi antara ROS 2 Image dan OpenCV
        self.bridge = CvBridge()
        
        # Subscriber untuk menerima data gambar dari topik kamera (Dapat diremap via Launch File)
        self.subscription = self.create_subscription(
            Image,
            image_topic,
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
            
        # [MODIFIKASI] Variabel Set (Himpunan) untuk menyimpan ID unik dari objek yang telah dideteksi.
        # Set digunakan karena proses pencarian (lookup) sangat cepat O(1) dan otomatis mengabaikan duplikasi.
        self.seen_track_ids = set()

        self.get_logger().info('YOLO Node siap mendeteksi objek!')

    def image_callback(self, msg):
        """
        Fungsi callback yang dipicu setiap kali pesan gambar baru masuk.
        """
        try:
            # 1. KONVERSI PESAN ROS 2 KE OPENCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # 2. INFERENSI YOLOv11 DENGAN PELACAKAN (TRACKING)
            # [MODIFIKASI] Menggunakan .track() alih-alih pemanggilan langsung model().
            # Argumen persist=True memberitahu tracker untuk mengingat (mengingat jejak) objek 
            # dari frame sebelumnya di sepanjang siklus aliran data. Tanpa persist=True, tracker akan mereset ID.
            results = self.model.track(cv_image, persist=True, stream=True)
            
            # List untuk menampung metadata deteksi yang HANYA berisi objek baru
            new_detections_metadata = []
            
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
                    
                    # [MODIFIKASI] Ekstraksi track_id dari objek 'box'
                    # Ultralytics menyematkan ID pelacakan di dalam atribut '.id'.
                    # Jika objek belum terdeteksi secara stabil, .id bisa mengembalikan None.
                    if box.id is not None:
                        # Ekstraksi ID sebagai integer karena defaultnya adalah tensor
                        track_id = int(box.id[0])
                    else:
                        # Jika tracker gagal memberikan ID untuk box ini (misal frame pertama muncul belum yakin)
                        # Kita beri nilai sementara agar program tetap aman berjalan.
                        track_id = -1
                    
                    # Logika Filter ID Unik untuk mencegah duplikasi data telemetri
                    if track_id not in self.seen_track_ids and track_id != -1:
                        # Karena ID ini belum ada di dalam self.seen_track_ids, berarti objek ini BARU.
                        # Masukkan ke dalam memori set agar ke depannya tidak dianggap baru lagi.
                        self.seen_track_ids.add(track_id)
                        
                        # Simpan data deteksi ke dalam list metadata untuk dipublikasikan JSON-nya.
                        # Di sini kita juga bisa menyertakan track_id-nya.
                        new_detections_metadata.append({
                            'track_id': track_id,
                            'class': label,
                            'confidence': round(conf, 2)
                        })
                    
                    # 4. MENGGAMBAR KE FRAME
                    # Anotasi box dan label tetap digambar untuk SEMUA objek (baik baru maupun lama)
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Menambahkan ID ke dalam teks display agar proses pelacakan terlihat di image
                    display_text = f"ID:{track_id} {label} {conf:.2f}"
                    cv2.putText(cv_image, display_text, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 5. PUBLIKASI METADATA (JSON)
            # HANYA kirim jika ada objek baru terdeteksi di frame ini.
            # Ini akan menghemat bandwidth topik /seatrack/detection/data drastis.
            if len(new_detections_metadata) > 0:
                json_msg = String()
                json_msg.data = json.dumps(new_detections_metadata)
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