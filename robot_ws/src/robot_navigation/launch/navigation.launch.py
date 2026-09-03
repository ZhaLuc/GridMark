                      
"""Launch Nav2 navigation stack with this package's parameter file."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description() -> LaunchDescription:
    pkg_share = get_package_share_directory('robot_navigation')
    default_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    nav2_bringup_share = get_package_share_directory('nav2_bringup')
    navigation_launch = os.path.join(
        nav2_bringup_share, 'launch', 'navigation_launch.py'
    )

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Full path to the Nav2 parameter YAML file',
    )
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true',
    )
    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the Nav2 stack',
    )
    declare_use_composition = DeclareLaunchArgument(
        'use_composition',
        default_value='False',
        description='Use composed bringup if true',
    )
    declare_container = DeclareLaunchArgument(
        'container_name',
        default_value='nav2_container',
        description='Container name when using composition',
    )

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    use_composition = LaunchConfiguration('use_composition')
    container_name = LaunchConfiguration('container_name')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'use_composition': use_composition,
            'container_name': container_name,
        }.items(),
    )

    return LaunchDescription([
        declare_params,
        declare_use_sim_time,
        declare_autostart,
        declare_use_composition,
        declare_container,
        nav2,
    ])
