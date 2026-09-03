                      
"""
Full-system bringup for the GridMark.

Startup order (gated on topic readiness where noted):
  1) serial bridge (/cmd_vel ↔ Mega, publishes /odom)
  2) rplidar_ros (/scan)
  3) wait until /odom and /scan are alive
  4) slam.launch.py (/map, map→odom, base→lidar TF)
  5) wait until /map is publishing
  6) navigation.launch.py + perception.launch.py
     + frontier_explorer_node + mission_node
     (+ base_link→camera_link static TF for mission projection)
"""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def _wait_for_topics(topics: list, name: str, timeout_sec: int = 120) -> ExecuteProcess:
    """
    Block until each topic appears in `ros2 topic list`, then exit 0.

    Used as a gate so SLAM does not start before /odom+/scan exist, and Nav2 /
    explorer do not start before /map exists.
    """
    checks = ' && '.join(
        [f'ros2 topic list | grep -Fxq "{t}"' for t in topics]
    )
    script = (
        f'echo "[bringup] waiting for {", ".join(topics)} (timeout {timeout_sec}s)"; '
        f'elapsed=0; '
        f'until {checks}; do '
        f' sleep 1; elapsed=$((elapsed+1)); '
        f' if [ "$elapsed" -ge {timeout_sec} ]; then '
        f' echo "[bringup] ERROR: timeout waiting for topics"; exit 1; '
        f' fi; '
        f'done; '
        f'echo "[bringup] topics ready: {", ".join(topics)}"'
    )
    return ExecuteProcess(
        cmd=['bash', '-c', script],
        name=name,
        output='screen',
    )

def generate_launch_description() -> LaunchDescription:
    use_sim_time = LaunchConfiguration('use_sim_time')
    serial_port = LaunchConfiguration('serial_port')
    lidar_port = LaunchConfiguration('lidar_port')
    lidar_x = LaunchConfiguration('lidar_x')
    lidar_y = LaunchConfiguration('lidar_y')
    lidar_z = LaunchConfiguration('lidar_z')
    camera_x = LaunchConfiguration('camera_x')
    camera_y = LaunchConfiguration('camera_y')
    camera_z = LaunchConfiguration('camera_z')

    bridge_share = get_package_share_directory('robot_bridge')
    slam_share = get_package_share_directory('robot_slam')
    nav_share = get_package_share_directory('robot_navigation')
    perception_share = get_package_share_directory('robot_perception')

                                                                        
                                           
                                                                        
    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bridge_share, 'launch', 'bridge.launch.py')
        ),
    )

                                                                        
                                                                   
                                                                        
    rplidar_node = Node(
