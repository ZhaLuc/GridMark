                      
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

        self._cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self._nav_client = ActionClient(self, NavigateToPose, action_name)
                                                               
        self._cancel_client = self.create_client(
            CancelGoal, f'{action_name}/_action/cancel_goal'
        )
        self._navigate_action = action_name

        map_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(OccupancyGrid, map_topic, self._on_map, map_qos)
        self.create_subscription(Detection2DArray, '/detections', self._on_detections, 10)
        self.create_subscription(Bool, '/exploration_complete', self._on_exploration_complete, 10)

        if self.use_depth:
                                                                                   
            self.create_subscription(Image, self.depth_topic, self._on_depth, 10)
            self.get_logger().info(
                f'use_depth=True: sampling depth from {self.depth_topic}'
            )
        else:
            self.get_logger().info(
                'use_depth=False: using no-depth bearing + ground-plane / '
                'assumed_range_m projection (project spec fallback)'
            )

        os.makedirs(self.output_dir, exist_ok=True)
        self.get_logger().info(
            f'mission_node watching class="{self.target_class}" '
            f'conf>={self.conf_thresh}, N={self.consecutive_required}'
        )

                                                                        
               
                                                                        

    def _on_map(self, msg: OccupancyGrid) -> None:
        self._latest_map = msg

    def _on_depth(self, msg: Image) -> None:
        self._latest_depth = msg

    def _on_exploration_complete(self, msg: Bool) -> None:
        if msg.data:
            self.get_logger().info(
                'Exploration complete signal received '
                '(mission still waits for a confirmed target detection).'
            )

    def _on_detections(self, msg: Detection2DArray) -> None:
        if self._mission_complete:
            return

        best = self._best_target_detection(msg)
        if best is None:
            self._consecutive_hits = 0
            self._estimate_buffer.clear()
            return

        estimate = self._estimate_target_map_xy(best)
        if estimate is None:
            self._consecutive_hits = 0
            self._estimate_buffer.clear()
            return

        self._consecutive_hits += 1
        self._estimate_buffer.append(estimate)
        self.get_logger().info(
            f'Target hit {self._consecutive_hits}/{self.consecutive_required} '
            f'at map approx ({estimate[0]:.2f}, {estimate[1]:.2f})'
        )

        if self._consecutive_hits < self.consecutive_required:
            return

                                                                   
        n = min(len(self._estimate_buffer), self.consecutive_required)
        xs = [p[0] for p in self._estimate_buffer[-n:]]
        ys = [p[1] for p in self._estimate_buffer[-n:]]
        target_xy = (sum(xs) / n, sum(ys) / n)
        self._confirm_and_stop(target_xy)

    def _best_target_detection(self, msg: Detection2DArray) -> Optional[Detection2D]:
        best: Optional[Detection2D] = None
        best_score = -1.0
        for det in msg.detections:
            for res in det.results:
                class_id = str(res.hypothesis.class_id)
                score = float(res.hypothesis.score)
                if class_id != self.target_class:
                    continue
                if score < self.conf_thresh:
                    continue
                if score > best_score:
                    best_score = score
                    best = det
        return best

                                                                        
                                  
                                                                        

    def _estimate_target_map_xy(
        self,
        det: Detection2D,
    ) -> Optional[Tuple[float, float]]:
        """
        Estimate target position in the map frame from a 2D detection.

        Pipeline:
          1) Pixel (u, v) = bbox center in the image.
          2) Build a unit bearing ray in the camera optical frame from intrinsics.
          3) Obtain range along that ray (depth image OR no-depth fallback).
          4) Scale the ray to a 3D point in camera_link, transform to map.
        """
        u = float(det.bbox.center.x)
        v = float(det.bbox.center.y)

                                                               
                                                                                 
                                                                         
                                                                                             
         
                                                                                   
                                                                        
                                                                        
