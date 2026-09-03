from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_mission'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools', 'Pillow'],
    zip_safe=True,
    maintainer='Lucas Zhang',
    maintainer_email='lucaszhang1118@gmail.com',
    description='Mission node: detection → map coordinate → stop robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_node = robot_mission.mission_node:main',
        ],
    },
)
