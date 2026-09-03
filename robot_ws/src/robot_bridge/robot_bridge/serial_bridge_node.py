                      
"""Serial bridge: /cmd_vel → Arduino PWM, ODOM ticks → /odom + TF."""

from __future__ import annotations

import math
import threading
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

try:
    import serial
    from serial import SerialException
except ImportError as exc: 
    raise SystemExit(
        'pyserial is required for robot_bridge.serial_bridge_node '
        '(pip install pyserial / apt install python3-serial)'
    ) from exc

def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    """Return (x, y, z, w) for a pure yaw rotation."""
    half = 0.5 * yaw
    return (0.0, 0.0, math.sin(half), math.cos(half))

class SerialBridgeNode(Node):
    """Bridge Jetson ROS 2 topics to the Mega firmware over USB serial."""

    def __init__(self) -> None:
        super().__init__('serial_bridge_node')

                                                                  
                                                                          
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('ticks_per_revolution', 1440.0)
        self.declare_parameter('wheel_radius_m', 0.0325)
        self.declare_parameter('track_width_m', 0.20)
                                                                                   
                                                                          
        self.declare_parameter('max_wheel_speed_mps', 0.6)
        self.declare_parameter('cmd_send_hz', 20.0)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        self._port_name = str(self.get_parameter('serial_port').value)
        self._baud = int(self.get_parameter('baud_rate').value)
        self._ticks_per_rev = float(self.get_parameter('ticks_per_revolution').value)
        self._wheel_radius = float(self.get_parameter('wheel_radius_m').value)
        self._track_width = float(self.get_parameter('track_width_m').value)
        self._max_wheel_speed = float(self.get_parameter('max_wheel_speed_mps').value)
        self._cmd_hz = float(self.get_parameter('cmd_send_hz').value)
        self._odom_frame = str(self.get_parameter('odom_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)

        self._lock = threading.Lock()
        self._latest_cmd = Twist()
        self._x = 0.0
        self._y = 0.0
        self._theta = 0.0
        self._v = 0.0
        self._omega = 0.0

        self._serial: Optional[serial.Serial] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._rx_running = False
        self._rx_buffer = ''

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._odom_pub = self.create_publisher(Odometry, '/odom', qos)
        self._tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel, qos)

        self._open_serial()

        period = 1.0 / self._cmd_hz if self._cmd_hz > 0.0 else 0.05
        self._cmd_timer = self.create_timer(period, self._on_cmd_timer)

        self.get_logger().info(
            f'serial_bridge_node on {self._port_name} @ {self._baud}; '
            f'TPR={self._ticks_per_rev}, R={self._wheel_radius}, '
            f'track={self._track_width}, vmax={self._max_wheel_speed}'
        )

    def _open_serial(self) -> None:
        try:
            self._serial = serial.Serial(
                port=self._port_name,
                baudrate=self._baud,
                timeout=0.05,
                write_timeout=0.05,
            )
                                                    
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
        except SerialException as exc:
            self.get_logger().error(f'Failed to open serial port {self._port_name}: {exc}')
            self._serial = None
            return

        self._rx_running = True
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()

    def _on_cmd_vel(self, msg: Twist) -> None:
        with self._lock:
            self._latest_cmd = msg

    def _twist_to_pwm(self, linear_x: float, angular_z: float) -> tuple[int, int]:
        """
        Inverse of firmware forward kinematics, then scale wheel speeds to PWM.

        Firmware forward:
          v = 0.5 * (v_l + v_r)
          omega = (v_r - v_l) / track_width
        Inverse:
          v_l = v - omega * track_width / 2
          v_r = v + omega * track_width / 2
        """
        half_track = 0.5 * self._track_width
        v_left = linear_x - angular_z * half_track
        v_right = linear_x + angular_z * half_track

        def speed_to_pwm(speed_mps: float) -> int:
            if self._max_wheel_speed <= 0.0:
                return 0
            scaled = (speed_mps / self._max_wheel_speed) * 255.0
            pwm = int(round(scaled))
            return max(-255, min(255, pwm))

        return speed_to_pwm(v_left), speed_to_pwm(v_right)

    def _on_cmd_timer(self) -> None:
        with self._lock:
            cmd = self._latest_cmd

        left_pwm, right_pwm = self._twist_to_pwm(cmd.linear.x, cmd.angular.z)
        line = f'L{left_pwm} R{right_pwm}\n'

        if self._serial is None or not self._serial.is_open:
            return
        try:
            self._serial.write(line.encode('ascii'))
        except SerialException as exc:
            self.get_logger().error(f'Serial write failed: {exc}')

    def _rx_loop(self) -> None:
        while self._rx_running and self._serial is not None:
            try:
                raw = self._serial.read(128)
            except SerialException as exc:
                self.get_logger().error(f'Serial read failed: {exc}')
                break
            if not raw:
                continue
            try:
                text = raw.decode('ascii', errors='ignore')
            except Exception: 
                continue
            self._rx_buffer += text
            while '\n' in self._rx_buffer:
                line, self._rx_buffer = self._rx_buffer.split('\n', 1)
                line = line.strip()
                if line:
                    self._handle_serial_line(line)

    def _handle_serial_line(self, line: str) -> None:
        if not line.startswith('ODOM'):
            return
        parts = line.split()
                                                             
        if len(parts) != 4:
            self.get_logger().warn(f'Ignoring malformed ODOM line: {line!r}')
            return
        try:
            d_left = int(parts[1])
            d_right = int(parts[2])
            dt_ms = float(parts[3])
        except ValueError:
            self.get_logger().warn(f'Ignoring non-numeric ODOM line: {line!r}')
            return

        if dt_ms <= 0.0 or self._ticks_per_rev <= 0.0:
            return

        dt_s = dt_ms * 0.001
                                                                                 
        meters_per_tick = (2.0 * math.pi * self._wheel_radius) / self._ticks_per_rev
        dist_left = d_left * meters_per_tick
        dist_right = d_right * meters_per_tick

        dist = 0.5 * (dist_left + dist_right)
        dtheta = (dist_right - dist_left) / self._track_width if self._track_width > 0.0 else 0.0

                                                              
        with self._lock:
            theta_mid = self._theta + 0.5 * dtheta
            self._x += dist * math.cos(theta_mid)
            self._y += dist * math.sin(theta_mid)
            self._theta += dtheta
                               
            self._theta = math.atan2(math.sin(self._theta), math.cos(self._theta))
            self._v = dist / dt_s
            self._omega = dtheta / dt_s
            x, y, theta = self._x, self._y, self._theta
            v, omega = self._v, self._omega

        self._publish_odometry(x, y, theta, v, omega)

    def _publish_odometry(
        self,
        x: float,
        y: float,
        theta: float,
        v: float,
        omega: float,
    ) -> None:
        stamp = self.get_clock().now().to_msg()
        q_x, q_y, q_z, q_w = yaw_to_quaternion(theta)

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self._odom_frame
        odom.child_frame_id = self._base_frame

        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.x = q_x
        odom.pose.pose.orientation.y = q_y
        odom.pose.pose.orientation.z = q_z
        odom.pose.pose.orientation.w = q_w

                                                                      
                                                                          
                                                                       
                                                                                         
        pose_cov = [0.0] * 36
        pose_cov[0] = 0.05 
        pose_cov[7] = 0.05 
        pose_cov[14] = 1e6 
        pose_cov[21] = 1e6 
        pose_cov[28] = 1e6 
        pose_cov[35] = 0.1 
        odom.pose.covariance = pose_cov

        odom.twist.twist.linear.x = v
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.angular.z = omega

        twist_cov = [0.0] * 36
        twist_cov[0] = 0.02 
        twist_cov[7] = 1e6 
        twist_cov[14] = 1e6 
        twist_cov[21] = 1e6 
        twist_cov[28] = 1e6 
        twist_cov[35] = 0.05 
        odom.twist.covariance = twist_cov

        self._odom_pub.publish(odom)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = stamp
        tf_msg.header.frame_id = self._odom_frame
        tf_msg.child_frame_id = self._base_frame
        tf_msg.transform.translation.x = x
        tf_msg.transform.translation.y = y
        tf_msg.transform.translation.z = 0.0
        tf_msg.transform.rotation.x = q_x
        tf_msg.transform.rotation.y = q_y
        tf_msg.transform.rotation.z = q_z
        tf_msg.transform.rotation.w = q_w
        self._tf_broadcaster.sendTransform(tf_msg)

    def destroy_node(self) -> bool:
        self._rx_running = False
        if self._rx_thread is not None and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=1.0)
        if self._serial is not None:
            try:
                                         
                self._serial.write(b'L0 R0\n')
                self._serial.close()
            except SerialException:
                pass
            self._serial = None
        return super().destroy_node()

def main(args=None) -> None:
    rclpy.init(args=args)
    node = SerialBridgeNode()
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
