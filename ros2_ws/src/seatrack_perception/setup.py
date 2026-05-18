from setuptools import find_packages, setup

package_name = 'seatrack_perception'

setup(
    name=package_name,
    version='0.0.0',
    # Mencari package secara otomatis di folder src
    packages=find_packages(exclude=['test']),
    data_files=[
        # Registrasi package ke dalam index ROS 2
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Menyertakan package.xml agar terdeteksi oleh sistem build colcon
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hadryan',
    maintainer_email='dimassaputraa779@gmail.com',
    description='Package untuk pengolahan citra dan deteksi sampah SeaTrack.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # Mendefinisikan perintah eksekusi untuk camera_node
            # Format: 'nama_alias = package.file:fungsi_utama'
            'camera_node = seatrack_perception.camera_node:main',
            'yolo_node = seatrack_perception.yolo_node:main',
            'telemetry_node = seatrack_perception.telemetry_node:main',
        ],
    },
)
