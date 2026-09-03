                      
"""YOLO26 TensorRT detector: /image_raw → /detections (Detection2DArray)."""

from __future__ import annotations

import os
from typing import Any, Optional

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

class YoloDetectorNode(Node):
    """Rate-limited Ultralytics YOLO inference on USB camera frames."""

    def __init__(self) -> None:
        super().__init__('yolo_detector_node')

        self.declare_parameter('weights_path', 'models/target_object_n.pt')
        self.declare_parameter('confidence_threshold', 0.6)
        self.declare_parameter('inference_hz', 8.0)
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('detections_topic', '/detections')
        self.declare_parameter('device', 0)
                                                                                   
        self.declare_parameter('class_names', [''])

        self._weights_path = str(self.get_parameter('weights_path').value)
        self._conf = float(self.get_parameter('confidence_threshold').value)
        self._inference_hz = float(self.get_parameter('inference_hz').value)
        self._image_topic = str(self.get_parameter('image_topic').value)
        self._detections_topic = str(self.get_parameter('detections_topic').value)
        self._device = self.get_parameter('device').value
        class_names = list(self.get_parameter('class_names').value)
        self._class_filter = {n for n in class_names if n}

        self._bridge = CvBridge()
        self._model: Any = None
        self._latest_image: Optional[Image] = None
        self._min_period = (
            1.0 / self._inference_hz if self._inference_hz > 0.0 else 0.125
        )

        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(Image, self._image_topic, self._on_image, image_qos)
        self._pub = self.create_publisher(Detection2DArray, self._detections_topic, 10)
        self.create_timer(self._min_period, self._on_timer)

        self._load_model()
        self.get_logger().info(
            f'yolo_detector_node ready: weights={self._weights_path}, '
            f'conf>={self._conf}, inference_hz={self._inference_hz} '
            f'(rate-limited for GPU sharing with SLAM/Nav2 on Orin Nano)'
        )

    def _load_model(self) -> None:
        weights = self._weights_path
        if not os.path.isabs(weights):
                                                                                
                                                                                 
            weights = os.path.abspath(weights)

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            self.get_logger().error(
                'ultralytics is not installed. On the Jetson: '
                'pip install ultralytics (and ensure TensorRT is available).'
            )
            raise SystemExit(1) from exc

        if not os.path.isfile(weights):
