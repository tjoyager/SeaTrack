#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import requests
import time

class TelemetryNode(Node):
    """
    Node ROS 2 yang bertugas mengirimkan metadata deteksi ke Backend FastAPI.
    Berfungsi sebagai jembatan (bridge) antara ekosistem ROS 2 dan Web API.
    """
    def __init__(self):
        super().__init__('telemetry_node')
        
        # Subscriber untuk menerima data JSON dari yolo_node
        self.subscription = self.create_subscription(
            String,
            '/seatrack/detection/data',
            self.listener_callback,
            10)
            
        # URL Backend FastAPI
        self.api_url = "http://127.0.0.1:8000/telemetry/"
        
        # Logika Rate Limiting
        self.last_send_time = 0
        self.send_interval = 2.0  # Minimal 2 detik sekali
        
        self.get_logger().info('Telemetry Node aktif dengan perbaikan payload schema.')

    def listener_callback(self, msg):
        """
        Fungsi callback untuk memproses data deteksi dan mengirimkannya ke backend.
        """
        current_time = time.time()
        
        # 1. CEK RATE LIMIT (SINKRONISASI FREKUENSI)
        if (current_time - self.last_send_time) < self.send_interval:
            return

        try:
            # 2. PARSING DATA JSON
            detections = json.loads(msg.data)
            
            if not detections:
                return

            # Flag untuk mencatat apakah setidaknya ada satu pengiriman berhasil
            any_success = False

            # 3. KIRIM DATA KE BACKEND
            # Karena API (TelemetryCreate) menerima satu objek deteksi per request,
            # kita melakukan iterasi pada setiap objek yang ditemukan di frame ini.
            for det in detections:
                # Menyiapkan payload agar SESUAI PERSIS dengan Pydantic TelemetryCreate
                # Kita menambahkan dummy latitude & longitude sesuai permintaan.
                payload = {
                    "latitude": 0.0,                    # Dummy latitude (float)
                    "longitude": 0.0,                   # Dummy longitude (float)
                    "object_class": det['class'],      # Nama class (string)
                    "confidence_score": det['confidence'] # Skor confidence (float)
                }
                
                # Melakukan POST request
                response = requests.post(self.api_url, json=payload, timeout=1.0)
                
                # 4. LOGGING DAN VALIDASI
                if response.status_code == 201:
                    self.get_logger().info(f"Berhasil: [{payload['object_class']}] tersimpan ke database.")
                    any_success = True
                else:
                    # MENCETAK DETAIL ERROR (Penting untuk debug 422 Unprocessable Entity)
                    # response.text akan berisi detail field mana yang salah menurut Pydantic di FastAPI.
                    self.get_logger().error(
                        f"Gagal kirim! Status: {response.status_code} | "
                        f"Detail: {response.text}"
                    )

            # Update waktu pengiriman terakhir jika ada data yang berhasil dikirim di frame ini
            if any_success:
                self.last_send_time = current_time

        except json.JSONDecodeError:
            self.get_logger().error('Gagal parsing JSON dari yolo_node.')
        except requests.exceptions.RequestException as e:
            self.get_logger().warn(f'Koneksi backend gagal: {str(e)}. Pastikan FastAPI aktif!')

def main(args=None):
    rclpy.init(args=args)
    telemetry_node = TelemetryNode()
    try:
        rclpy.spin(telemetry_node)
    except KeyboardInterrupt:
        pass
    finally:
        telemetry_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
