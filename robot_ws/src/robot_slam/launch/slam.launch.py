                      
"""Launch slam_toolbox (online async) and base_link → lidar_link static TF."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description() -> LaunchDescription:
    pkg_share = get_package_share_directory('robot_slam')
    default_params = os.path.join(pkg_share, 'config', 'slam_toolbox_params.yaml')

    slam_toolbox_share = get_package_share_directory('slam_toolbox')
    online_async_launch = os.path.join(
        slam_toolbox_share, 'launch', 'online_async_launch.py'
    )

                                                                      
                                                                            
                                                                                
                                                   
    declare_lidar_x = DeclareLaunchArgument(
        'lidar_x',
        default_value='0.10',
        description='base_link → lidar_link translation x (m), forward',
    )
    declare_lidar_y = DeclareLaunchArgument(
        'lidar_y',
        default_value='0.00',
        description='base_link → lidar_link translation y (m), left',
    )
    declare_lidar_z = DeclareLaunchArgument(
        'lidar_z',
        default_value='0.15',
        description='base_link → lidar_link translation z (m), up',
    )
    declare_lidar_yaw = DeclareLaunchArgument(
        'lidar_yaw',
        default_value='0.0',
        description='base_link → lidar_link yaw (rad)',
    )
    declare_lidar_pitch = DeclareLaunchArgument(
        'lidar_pitch',
        default_value='0.0',
        description='base_link → lidar_link pitch (rad)',
    )
    declare_lidar_roll = DeclareLaunchArgument(
        'lidar_roll',
        default_value='0.0',
        description='base_link → lidar_link roll (rad)',
    )
    declare_params = DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_params,
        description='Full path to slam_toolbox parameter YAML',
    )
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use /clock (sim) instead of wall time',
    )

    lidar_x = LaunchConfiguration('lidar_x')
    lidar_y = LaunchConfiguration('lidar_y')
    lidar_z = LaunchConfiguration('lidar_z')
    lidar_yaw = LaunchConfiguration('lidar_yaw')
    lidar_pitch = LaunchConfiguration('lidar_pitch')
    lidar_roll = LaunchConfiguration('lidar_roll')
    slam_params_file = LaunchConfiguration('slam_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    base_to_lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_lidar_tf',
        output='screen',
        arguments=[
            '--x', lidar_x,
            '--y', lidar_y,
            '--z', lidar_z,
            '--yaw', lidar_yaw,
            '--pitch', lidar_pitch,
            '--roll', lidar_roll,
            '--frame-id', 'base_link',
            '--child-frame-id', 'lidar_link',
        ],
    )

    slam_online_async = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(online_async_launch),
        launch_arguments={
            'slam_params_file': slam_params_file,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    return LaunchDescription([
        declare_lidar_x,
        declare_lidar_y,
        declare_lidar_z,
        declare_lidar_yaw,
        declare_lidar_pitch,
        declare_lidar_roll,
        declare_params,
        declare_use_sim_time,
        base_to_lidar_tf,
        slam_online_async,
    ])
