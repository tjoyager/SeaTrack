#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import requests
import time
import psutil

class TelemetryNode(Node):
    """
    Node ROS 2 yang bertugas mengirimkan metadata deteksi dan 
    kesehatan sistem (CPU/RAM) ke Backend FastAPI.
    """
    def __init__(self):
        super().__init__('telemetry_node')
        
        # 1. Subscriber untuk Data Deteksi
        self.subscription = self.create_subscription(
            String,
            '/seatrack/detection/data',
            self.listener_callback,
            10)
            
        # 2. Konfigurasi API
        self.api_base_url = "http://127.0.0.1:8000"
        self.telemetry_url = f"{self.api_base_url}/telemetry/"
        self.health_url = f"{self.api_base_url}/system-health/"
        
        # 3. Timer untuk Monitoring Sistem (Kirim data health setiap 5 detik)
        self.health_timer = self.create_timer(5.0, self.send_system_health)
        
        # Logika Rate Limiting untuk Deteksi
        self.last_send_time = 0
        self.send_interval = 2.0
        
        self.get_logger().info('Telemetry Node aktif dengan fitur Health Monitoring.')

    def send_system_health(self):
        """
        Mengambil data CPU/RAM dan mengirimkannya ke endpoint /system-health/
        """
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            payload = {
                "cpu_usage": float(cpu),
                "ram_usage": float(ram)
            }
            
            response = requests.post(self.health_url, json=payload, timeout=1.0)
            
            if response.status_code == 201:
                # Log status setiap kali kirim (bisa dimatikan jika terlalu berisik)
                # self.get_logger().info(f"Health Sent: CPU {cpu}% | RAM {ram}%")
                pass
            else:
                self.get_logger().error(f"Gagal kirim Health! Status: {response.status_code}")
                
        except Exception as e:
            self.get_logger().warn(f"Gagal monitor sistem: {str(e)}")

    def listener_callback(self, msg):
        """
        Fungsi callback untuk memproses data deteksi.
        """
        current_time = time.time()
        
        if (current_time - self.last_send_time) < self.send_interval:
            return

        try:
            detections = json.loads(msg.data)
            if not detections:
                return

            any_success = False
            for det in detections:
                payload = {
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "object_class": det['class'],
                    "confidence_score": det['confidence']
                }
                
                response = requests.post(self.telemetry_url, json=payload, timeout=1.0)
                
                if response.status_code == 201:
                    self.get_logger().info(f"Berhasil: [{payload['object_class']}] tersimpan ke database.")
                    any_success = True

            if any_success:
                self.last_send_time = current_time

        except json.JSONDecodeError:
            self.get_logger().error('Gagal parsing JSON dari yolo_node.')
        except requests.exceptions.RequestException as e:
            self.get_logger().warn(f'Koneksi backend gagal: {str(e)}.')

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
