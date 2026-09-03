                      
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
        package='rplidar_ros',
        executable='rplidar_node',
        name='rplidar_node',
        output='screen',
        parameters=[{
            'serial_port': lidar_port,
            'serial_baudrate': 115200,
            'frame_id': 'lidar_link',
            'angle_compensate': True,
            'scan_mode': 'Standard',
            'topic_name': '/scan',
        }],
    )
    rplidar_delayed = TimerAction(
        period=2.0,
        actions=[
            LogInfo(msg='[bringup] starting rplidar_ros'),
            rplidar_node,
        ],
    )

                                                                        
                                                        
                                                                        
    wait_odom_scan_proc = _wait_for_topics(
        ['/odom', '/scan'], name='wait_odom_scan'
    )
    wait_odom_scan = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg='[bringup] gate: waiting for /odom and /scan'),
            wait_odom_scan_proc,
        ],
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_share, 'launch', 'slam.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'lidar_x': lidar_x,
            'lidar_y': lidar_y,
            'lidar_z': lidar_z,
        }.items(),
    )

    start_slam_when_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_odom_scan_proc,
            on_exit=[
                LogInfo(msg='[bringup] /odom and /scan alive - starting SLAM'),
                slam_launch,
            ],
        )
    )

                                                                        
                                                                         
                                                                        
    wait_map_proc = _wait_for_topics(
        ['/map'], name='wait_map', timeout_sec=180
    )
    wait_map = TimerAction(
        period=8.0,
        actions=[
            LogInfo(msg='[bringup] gate: waiting for /map from slam_toolbox'),
            wait_map_proc,
        ],
    )

    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_share, 'launch', 'navigation.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'autostart': 'true',
        }.items(),
    )

    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(perception_share, 'launch', 'perception.launch.py')
        ),
    )

                                                                      
                                                                     
    camera_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_camera_tf',
        output='screen',
        arguments=[
            '--x', camera_x,
            '--y', camera_y,
            '--z', camera_z,
            '--yaw', '0.0',
            '--pitch', '0.0',
            '--roll', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'camera_link',
        ],
    )

    frontier_explorer = Node(
        package='robot_navigation',
        executable='frontier_explorer_node',
        name='frontier_explorer_node',
        output='screen',
    )

    mission_node = Node(
        package='robot_mission',
        executable='mission_node',
        name='mission_node',
        output='screen',
        parameters=[{
            'target_class': 'target_object',
            'confidence_threshold': 0.6,
            'consecutive_required': 3,
            'use_depth': False,
            'output_dir': 'mission_outputs',
        }],
    )

    start_upper_stack_when_map_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_map_proc,
            on_exit=[
                LogInfo(
                    msg='[bringup] /map alive - starting Nav2, perception, '
                        'frontier explorer, mission'
                ),
                navigation_launch,
                perception_launch,
                camera_tf,
                TimerAction(
                    period=5.0,
                    actions=[frontier_explorer, mission_node],
                ),
            ],
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/ttyACM0',
            description='Arduino Mega USB serial device (configure in odom YAML too)',
        ),
        DeclareLaunchArgument(
            'lidar_port',
            default_value='/dev/ttyUSB0',
            description='RPLIDAR USB serial device',
        ),
        DeclareLaunchArgument('lidar_x', default_value='0.10'),
        DeclareLaunchArgument('lidar_y', default_value='0.00'),
        DeclareLaunchArgument('lidar_z', default_value='0.15'),
        DeclareLaunchArgument('camera_x', default_value='0.12'),
        DeclareLaunchArgument('camera_y', default_value='0.00'),
        DeclareLaunchArgument('camera_z', default_value='0.20'),
        LogInfo(msg='[bringup] full_system: starting serial bridge'),
        LogInfo(msg=['[bringup] configured serial_port=', serial_port]),
        bridge_launch,
        rplidar_delayed,
        wait_odom_scan,
        start_slam_when_ready,
        wait_map,
        start_upper_stack_when_map_ready,
    ])
