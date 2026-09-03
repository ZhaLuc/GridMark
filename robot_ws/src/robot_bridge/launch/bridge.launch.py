                      
"""Launch serial_bridge_node with odom calibration parameters."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description() -> LaunchDescription:
    pkg_share = get_package_share_directory('robot_bridge')
    calib_yaml = os.path.join(pkg_share, 'config', 'odom_calibration.yaml')

    bridge_node = Node(
        package='robot_bridge',
        executable='serial_bridge_node',
        name='serial_bridge_node',
        output='screen',
        parameters=[calib_yaml],
    )

    return LaunchDescription([bridge_node])
