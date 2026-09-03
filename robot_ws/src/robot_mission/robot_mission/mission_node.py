                      
"""
Mission fusion node.

On confirmed target detections: estimate map-frame (x, y), stop the robot,
cancel Nav2 NavigateToPose, and save an annotated /map PNG.
"""

from __future__ import annotations

import math
import os
from datetime import datetime
from typing import List, Optional, Tuple

import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import PointStamped, Twist
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from vision_msgs.msg import Detection2D, Detection2DArray
from tf2_ros import Buffer, TransformListener, TransformException
                                                                        
import tf2_geometry_msgs 

try:
    from PIL import Image as PilImage
    from PIL import ImageDraw
except ImportError as exc: 
    raise SystemExit(
        'Pillow is required for robot_mission.mission_node '
        '(pip install Pillow / apt install python3-pil)'
    ) from exc

class MissionNode(Node):
    """Detect target → map coordinate → stop + annotate map."""

    def __init__(self) -> None:
        super().__init__('mission_node')

                                       
        self.declare_parameter('target_class', 'target_object')
        self.declare_parameter('confidence_threshold', 0.6)
        self.declare_parameter('consecutive_required', 3)

                        
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_link')

                                                                           
                                                                          
                                                                             
                                                                                
        self.declare_parameter('image_width', 640)
        self.declare_parameter('image_height', 480)
        self.declare_parameter('fx', 600.0)
        self.declare_parameter('fy', 600.0)
        self.declare_parameter('cx', 320.0)
        self.declare_parameter('cy', 240.0)

                                                                 
                                                                    
                                                                 
                                                                      
        self.declare_parameter('target_height_m', 0.05)
        self.declare_parameter('assumed_range_m', 1.5)
        self.declare_parameter('min_range_m', 0.3)
        self.declare_parameter('max_range_m', 5.0)

                                                                
        self.declare_parameter('use_depth', False)
        self.declare_parameter('depth_topic', '/camera/aligned_depth_to_color/image_raw')
        self.declare_parameter('depth_scale_m', 0.001) 

                                
        self.declare_parameter('output_dir', 'mission_outputs')
        self.declare_parameter('navigate_action', 'navigate_to_pose')
        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('tf_timeout_s', 0.5)

        self.target_class = str(self.get_parameter('target_class').value)
        self.conf_thresh = float(self.get_parameter('confidence_threshold').value)
        self.consecutive_required = int(self.get_parameter('consecutive_required').value)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.base_frame = str(self.get_parameter('base_frame').value)
        self.camera_frame = str(self.get_parameter('camera_frame').value)
        self.image_width = int(self.get_parameter('image_width').value)
        self.image_height = int(self.get_parameter('image_height').value)
        self.fx = float(self.get_parameter('fx').value)
        self.fy = float(self.get_parameter('fy').value)
        self.cx = float(self.get_parameter('cx').value)
        self.cy = float(self.get_parameter('cy').value)
        self.target_height_m = float(self.get_parameter('target_height_m').value)
        self.assumed_range_m = float(self.get_parameter('assumed_range_m').value)
        self.min_range_m = float(self.get_parameter('min_range_m').value)
        self.max_range_m = float(self.get_parameter('max_range_m').value)
        self.use_depth = bool(self.get_parameter('use_depth').value)
        self.depth_topic = str(self.get_parameter('depth_topic').value)
        self.depth_scale_m = float(self.get_parameter('depth_scale_m').value)
        self.output_dir = str(self.get_parameter('output_dir').value)
        action_name = str(self.get_parameter('navigate_action').value)
        map_topic = str(self.get_parameter('map_topic').value)
        self.tf_timeout = float(self.get_parameter('tf_timeout_s').value)

        self._consecutive_hits = 0
        self._mission_complete = False
        self._latest_map: Optional[OccupancyGrid] = None
        self._latest_depth: Optional[Image] = None
        self._estimate_buffer: List[Tuple[float, float]] = []

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

