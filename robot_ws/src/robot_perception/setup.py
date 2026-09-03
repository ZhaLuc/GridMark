from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'models'), [
            f for f in glob('models/*')
            if f.lower().endswith(('.pt', '.onnx', '.engine', '.md'))
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Lucas Zhang',
    maintainer_email='lucaszhang1118@gmail.com',
    description='YOLO26 TensorRT detection and usb_cam launch for the SLAM robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_detector_node = robot_perception.yolo_detector_node:main',
        ],
    },
)
