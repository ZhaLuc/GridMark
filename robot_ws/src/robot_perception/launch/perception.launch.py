                      
"""Launch usb_cam (/image_raw) and the YOLO26 TensorRT detector."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description() -> LaunchDescription:
    pkg_share = get_package_share_directory('robot_perception')
    default_engine = os.path.join(pkg_share, 'models', 'target_object_n.pt')
    default_cam_params = os.path.join(pkg_share, 'config', 'usb_cam_params.yaml')

    declare_weights = DeclareLaunchArgument(
        'weights_path',
        default_value=default_engine,
        description='Path to YOLO26 weights (.pt, .onnx, or TensorRT .engine)',
    )
    declare_conf = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.6',
        description='Minimum detection confidence',
    )
    declare_hz = DeclareLaunchArgument(
        'inference_hz',
        default_value='8.0',
        description='Max YOLO inference rate (Hz); keep modest on Orin Nano',
    )
    declare_video_device = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video0',
        description='V4L2 device for usb_cam',
    )
    declare_cam_params = DeclareLaunchArgument(
        'cam_params_file',
        default_value=default_cam_params,
        description='usb_cam parameter YAML',
    )

    weights_path = LaunchConfiguration('weights_path')
    confidence_threshold = LaunchConfiguration('confidence_threshold')
    inference_hz = LaunchConfiguration('inference_hz')
    video_device = LaunchConfiguration('video_device')
    cam_params_file = LaunchConfiguration('cam_params_file')

    usb_cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        output='screen',
        parameters=[
            cam_params_file,
            {
                'video_device': video_device,
                'camera_frame_id': 'camera_link',
            },
        ],
        remappings=[
            ('image_raw', '/image_raw'),
        ],
    )

    yolo_node = Node(
        package='robot_perception',
        executable='yolo_detector_node',
        name='yolo_detector_node',
        output='screen',
        parameters=[{
            'weights_path': weights_path,
            'confidence_threshold': confidence_threshold,
            'inference_hz': inference_hz,
            'image_topic': '/image_raw',
            'detections_topic': '/detections',
            'device': 0,
        }],
    )

    return LaunchDescription([
        declare_weights,
        declare_conf,
        declare_hz,
        declare_video_device,
        declare_cam_params,
        usb_cam_node,
        yolo_node,
    ])
