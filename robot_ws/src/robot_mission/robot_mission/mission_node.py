                      
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

                                                               
                                                                                 
                                                                         
                                                                                             
         
                                                                                   
                                                                        
                                                                        
                                                                        
                                                                                       
         
                                                                          
                                           
                                        
                                      
         
                                             
                                                      
                                                      
                                                        
                                 
        x_n = (u - self.cx) / self.fx
        y_n = (v - self.cy) / self.fy
        d_opt_x, d_opt_y, d_opt_z = x_n, y_n, 1.0
        opt_norm = math.sqrt(d_opt_x ** 2 + d_opt_y ** 2 + d_opt_z ** 2)
        if opt_norm < 1e-9:
            return None
        d_opt_x /= opt_norm
        d_opt_y /= opt_norm
        d_opt_z /= opt_norm

                                                               
        d_link_x = d_opt_z
        d_link_y = -d_opt_x
        d_link_z = -d_opt_y

                                                   
        if self.use_depth:
            range_m = self._range_from_depth(u, v)
            if range_m is None:
                                                         
                range_m = self._range_from_ground_plane(d_link_x, d_link_y, d_link_z)
        else:
                                                                                
                                                                               
                                                                             
                                                       
            range_m = self._range_from_ground_plane(d_link_x, d_link_y, d_link_z)

        if range_m is None:
            return None
        range_m = max(self.min_range_m, min(self.max_range_m, range_m))

                                                                  
        point_cam = PointStamped()
        point_cam.header.stamp = self.get_clock().now().to_msg()
        point_cam.header.frame_id = self.camera_frame
        point_cam.point.x = d_link_x * range_m
        point_cam.point.y = d_link_y * range_m
        point_cam.point.z = d_link_z * range_m

        try:
            point_map = self._tf_buffer.transform(
                point_cam,
                self.map_frame,
                timeout=Duration(seconds=self.tf_timeout),
            )
        except TransformException as exc:
            self.get_logger().warn(f'TF camera→map failed: {exc}')
            return None

        return (float(point_map.point.x), float(point_map.point.y))

    def _range_from_ground_plane(
        self,
        d_link_x: float,
        d_link_y: float,
        d_link_z: float,
    ) -> Optional[float]:
        """
        No-depth fallback from the project spec.

        Transform the camera ray into the map frame and intersect with the
        horizontal plane z = target_height_m:

            origin_map + t * dir_map has z = target_height_m
            t = (target_height_m - origin_z) / dir_z

        If |dir_z| is tiny (ray nearly parallel to the ground), fall back to
        assumed_range_m measured along the camera ray.
        """
                                                           
        try:
            tf_cam = self._tf_buffer.lookup_transform(
                self.map_frame,
                self.camera_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=self.tf_timeout),
            )
        except TransformException as exc:
            self.get_logger().warn(f'TF lookup map←camera failed: {exc}')
            return self.assumed_range_m

        ox = tf_cam.transform.translation.x
        oy = tf_cam.transform.translation.y
        oz = tf_cam.transform.translation.z
        q = tf_cam.transform.rotation
                                                                                 
        dir_map = self._quat_rotate_vector(
            q.x, q.y, q.z, q.w, d_link_x, d_link_y, d_link_z
        )
        dz = dir_map[2]
        if abs(dz) < 1e-3:
                                                                      
            return self.assumed_range_m

        t = (self.target_height_m - oz) / dz
        if t < self.min_range_m:
            return self.assumed_range_m

                                                                               
                                                        
        if t > self.max_range_m:
            return self.assumed_range_m
        return t

    def _range_from_depth(self, u: float, v: float) -> Optional[float]:
        """
        Optional RealSense (aligned depth) path when self.use_depth is True.

        Samples the depth image at the bbox-center pixel and converts to meters.
        Returns None on missing frame, bad encoding, or invalid depth so the
        caller can fall back to the ground-plane method.
        """
        if self._latest_depth is None:
            return None

        depth_msg = self._latest_depth
        width = depth_msg.width
        height = depth_msg.height
        ui = int(round(u))
        vi = int(round(v))
        if ui < 0 or vi < 0 or ui >= width or vi >= height:
            return None

                                                                      
        vals: List[float] = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                x = ui + dx
                y = vi + dy
                if x < 0 or y < 0 or x >= width or y >= height:
                    continue
                z = self._read_depth_pixel(depth_msg, x, y)
                if z is not None and z > 0.0:
                    vals.append(z)
        if not vals:
            return None
        return sum(vals) / len(vals)

    def _read_depth_pixel(self, msg: Image, x: int, y: int) -> Optional[float]:
        enc = msg.encoding.lower()
        data = bytes(msg.data)
        try:
            if enc in ('16uc1', 'mono16'):
                                                                             
                byte_index = y * msg.step + x * 2
                raw = int.from_bytes(data[byte_index:byte_index + 2], byteorder='little')
                if raw == 0:
                    return None
                return raw * self.depth_scale_m
            if enc == '32fc1':
                import struct
                byte_index = y * msg.step + x * 4
                raw = struct.unpack_from('<f', data, byte_index)[0]
                if not math.isfinite(raw) or raw <= 0.0:
                    return None
                return float(raw)
        except Exception: 
            return None
        return None

    @staticmethod
    def _quat_rotate_vector(
        qx: float, qy: float, qz: float, qw: float,
        vx: float, vy: float, vz: float,
    ) -> Tuple[float, float, float]:
        """Rotate vector v by quaternion q (x,y,z,w)."""
                            
        ix = qw * vx + qy * vz - qz * vy
        iy = qw * vy + qz * vx - qx * vz
        iz = qw * vz + qx * vy - qy * vx
        iw = -qx * vx - qy * vy - qz * vz
        return (
            ix * qw + iw * -qx + iy * -qz - iz * -qy,
            iy * qw + iw * -qy + iz * -qx - ix * -qz,
            iz * qw + iw * -qz + ix * -qy - iy * -qx,
        )

                                                                        
                        
                                                                        

    def _confirm_and_stop(self, target_xy: Tuple[float, float]) -> None:
        self._mission_complete = True
        tx, ty = target_xy

        robot_xy = self._lookup_robot_map_xy()
        if robot_xy is not None:
            self.get_logger().info(
                f'Robot map pose at confirm: ({robot_xy[0]:.3f}, {robot_xy[1]:.3f}) m'
            )

                                                                     
        stop = Twist()
        self._cmd_pub.publish(stop)

                                                     
        self._cancel_navigation()

                                    
        self.get_logger().info(
            f'Target confirmed at map-frame ({tx:.3f}, {ty:.3f}) m - robot stopped'
        )

                                    
        if self._latest_map is not None:
            path = self._save_map_with_target(self._latest_map, tx, ty)
            if path:
                self.get_logger().info(f'Annotated map saved to {path}')
        else:
            self.get_logger().warn('No /map received yet; skipping PNG export')

    def _lookup_robot_map_xy(self) -> Optional[Tuple[float, float]]:
        """map → base_link translation (robot pose in the map frame)."""
        try:
            tf = self._tf_buffer.lookup_transform(
                self.map_frame,
                self.base_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=self.tf_timeout),
            )
        except TransformException as exc:
            self.get_logger().warn(f'TF {self.map_frame}→{self.base_frame} failed: {exc}')
            return None
        return (tf.transform.translation.x, tf.transform.translation.y)

    def _cancel_navigation(self) -> None:
        """Cancel all active NavigateToPose goals via the action cancel service."""
                                                                            
        if not self._cancel_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn(
                f'Cancel service {self._navigate_action}/_action/cancel_goal '
                'unavailable; relying on zero /cmd_vel'
            )
            return

        request = CancelGoal.Request()
        future = self._cancel_client.call_async(request)

        def _done(fut) -> None:
            try:
                result = fut.result()
                n = len(result.goals_canceling) if result is not None else 0
                self.get_logger().info(
                    f'Nav2 cancel requested; goals_canceling={n}'
                )
            except Exception as exc: 
                self.get_logger().warn(f'Nav2 cancel call failed: {exc}')

        future.add_done_callback(_done)

    def _save_map_with_target(
        self,
        grid: OccupancyGrid,
        target_x: float,
        target_y: float,
    ) -> Optional[str]:
        """
        Render OccupancyGrid to a PNG and mark the target as a red dot.

        Occupancy values: -1 unknown, 0 free, 100 occupied (typical).
        """
        width = grid.info.width
        height = grid.info.height
        if width <= 0 or height <= 0:
            return None

                                                                               
                                                               
        pixels = bytearray(width * height * 3)
        data = grid.data
        for my in range(height):
            for mx in range(width):
                val = int(data[my * width + mx])
                if val < 0:
                    r = g = b = 128 
                elif val == 0:
                    r = g = b = 255 
                else:
                                     
                    shade = max(0, 255 - int(val * 2.55))
                    r = g = b = shade
                                                               
                img_y = height - 1 - my
                i = (img_y * width + mx) * 3
                pixels[i] = r
                pixels[i + 1] = g
                pixels[i + 2] = b

        img = PilImage.frombytes('RGB', (width, height), bytes(pixels))
        draw = ImageDraw.Draw(img)

        res = grid.info.resolution
        ox = grid.info.origin.position.x
        oy = grid.info.origin.position.y
                          
        mx = (target_x - ox) / res
        my = (target_y - oy) / res
        ix = int(round(mx))
        iy_img = height - 1 - int(round(my))

        radius = max(3, int(0.15 / res)) 
        if 0 <= ix < width and 0 <= iy_img < height:
            draw.ellipse(
                (ix - radius, iy_img - radius, ix + radius, iy_img + radius),
                fill=(255, 0, 0),
                outline=(255, 0, 0),
            )

        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = os.path.join(self.output_dir, f'target_map_{stamp}.png')
        img.save(out_path)
        return out_path

def main(args=None) -> None:
    rclpy.init(args=args)
    node = MissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
