                      
"""Launch the mission fusion node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument('target_class', default_value='target_object'),
        DeclareLaunchArgument('confidence_threshold', default_value='0.6'),
        DeclareLaunchArgument('consecutive_required', default_value='3'),
        DeclareLaunchArgument('use_depth', default_value='false'),
        DeclareLaunchArgument('output_dir', default_value='mission_outputs'),
        Node(
            package='robot_mission',
            executable='mission_node',
            name='mission_node',
            output='screen',
            parameters=[{
                'target_class': LaunchConfiguration('target_class'),
                'confidence_threshold': ParameterValue(
                    LaunchConfiguration('confidence_threshold'), value_type=float
                ),
                'consecutive_required': ParameterValue(
                    LaunchConfiguration('consecutive_required'), value_type=int
                ),
                'use_depth': ParameterValue(
                    LaunchConfiguration('use_depth'), value_type=bool
                ),
                'output_dir': LaunchConfiguration('output_dir'),
            }],
        ),
    ])
