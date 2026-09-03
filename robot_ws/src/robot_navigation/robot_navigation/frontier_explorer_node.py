                      
"""Frontier exploration node: /map frontiers → Nav2 NavigateToPose goals."""

from __future__ import annotations

import math
from collections import deque
from typing import List, Optional, Sequence, Tuple

import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import Bool
from tf2_ros import Buffer, TransformListener, TransformException

GridIndex = Tuple[int, int] 

class FrontierExplorerNode(Node):
    """
    Subscribe to /map, find frontier cells (free adjacent to unknown), cluster
    them, and send the nearest cluster centroid to Nav2 NavigateToPose.
    """

                               
    UNKNOWN = -1
    FREE_MAX = 50 

    def __init__(self) -> None:
        super().__init__('frontier_explorer_node')

        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('min_frontier_size', 8)
        self.declare_parameter('goal_blacklist_radius_m', 0.45)
        self.declare_parameter('replan_period_s', 2.0)
        self.declare_parameter('tf_timeout_s', 0.5)
        self.declare_parameter('navigate_action', 'navigate_to_pose')

        self._map_topic = str(self.get_parameter('map_topic').value)
        self._map_frame = str(self.get_parameter('map_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)
        self._min_frontier_size = int(self.get_parameter('min_frontier_size').value)
        self._blacklist_radius = float(self.get_parameter('goal_blacklist_radius_m').value)
        self._replan_period = float(self.get_parameter('replan_period_s').value)
        self._tf_timeout = float(self.get_parameter('tf_timeout_s').value)
        action_name = str(self.get_parameter('navigate_action').value)

        map_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._map: Optional[OccupancyGrid] = None
        self._busy = False
        self._exploration_complete = False
        self._failed_goals: List[Tuple[float, float]] = []

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        self._nav_client = ActionClient(self, NavigateToPose, action_name)
        self._done_pub = self.create_publisher(Bool, '/exploration_complete', 10)
        self.create_subscription(OccupancyGrid, self._map_topic, self._on_map, map_qos)
        self.create_timer(self._replan_period, self._on_timer)

        self.get_logger().info(
            f'frontier_explorer_node listening on {self._map_topic}; '
            f'min_frontier_size={self._min_frontier_size}'
        )

    def _on_map(self, msg: OccupancyGrid) -> None:
        self._map = msg

    def _on_timer(self) -> None:
        if self._exploration_complete or self._busy:
            return
        if self._map is None:
            return
        if not self._nav_client.wait_for_server(timeout_sec=0.1):
            self.get_logger().debug('Waiting for NavigateToPose action server...')
            return

        robot_xy = self._lookup_robot_xy()
        if robot_xy is None:
            return

        goal_xy = self._select_frontier_goal(self._map, robot_xy)
        if goal_xy is None:
            self._finish_exploration()
            return

        self._send_goal(goal_xy[0], goal_xy[1], robot_xy)

    def _lookup_robot_xy(self) -> Optional[Tuple[float, float]]:
        try:
            tf = self._tf_buffer.lookup_transform(
                self._map_frame,
                self._base_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=self._tf_timeout),
            )
        except TransformException as exc:
            self.get_logger().warn(f'TF {self._map_frame}→{self._base_frame} failed: {exc}')
            return None
        return (tf.transform.translation.x, tf.transform.translation.y)

    def _finish_exploration(self) -> None:
        self._exploration_complete = True
        self.get_logger().info('Exploration complete')
        msg = Bool()
        msg.data = True
        self._done_pub.publish(msg)

    def _send_goal(
        self,
        gx: float,
        gy: float,
        robot_xy: Tuple[float, float],
    ) -> None:
        yaw = math.atan2(gy - robot_xy[1], gx - robot_xy[0])
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self._map_frame
        pose.pose.position.x = gx
        pose.pose.position.y = gy
        pose.pose.position.z = 0.0
        pose.pose.orientation.z = math.sin(0.5 * yaw)
        pose.pose.orientation.w = math.cos(0.5 * yaw)

        goal = NavigateToPose.Goal()
        goal.pose = pose

        self._busy = True
        self.get_logger().info(f'Sending frontier goal to ({gx:.2f}, {gy:.2f})')
        send_future = self._nav_client.send_goal_async(goal)
        send_future.add_done_callback(
            lambda fut, gxy=(gx, gy): self._on_goal_response(fut, gxy)
        )

    def _on_goal_response(self, future, goal_xy: Tuple[float, float]) -> None:
        goal_handle = future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().warn('NavigateToPose goal rejected')
            self._failed_goals.append(goal_xy)
            self._busy = False
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda fut, gxy=goal_xy: self._on_goal_result(fut, gxy)
        )

    def _on_goal_result(self, future, goal_xy: Tuple[float, float]) -> None:
        try:
            wrapped = future.result()
            status = wrapped.status
        except Exception as exc: 
            self.get_logger().error(f'NavigateToPose result error: {exc}')
            self._failed_goals.append(goal_xy)
            self._busy = False
            return

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Frontier goal succeeded')
        else:
            self.get_logger().warn(f'Frontier goal ended with status={status}; blacklisting')
            self._failed_goals.append(goal_xy)

        self._busy = False

                                                                        
                       
                                                                        

    def _select_frontier_goal(
        self,
        grid: OccupancyGrid,
        robot_xy: Tuple[float, float],
    ) -> Optional[Tuple[float, float]]:
        frontiers = self._find_frontier_cells(grid)
        if not frontiers:
            return None

        clusters = self._cluster_frontiers(frontiers)
        candidates: List[Tuple[float, float, int]] = []
        for cluster in clusters:
            if len(cluster) < self._min_frontier_size:
                continue
            cx, cy = self._cluster_centroid_world(grid, cluster)
            if self._is_blacklisted(cx, cy):
                continue
            candidates.append((cx, cy, len(cluster)))

        if not candidates:
            return None

        rx, ry = robot_xy

        def sort_key(item: Tuple[float, float, int]) -> Tuple[float, float]:
            cx, cy, size = item
            dist = math.hypot(cx - rx, cy - ry)
                                                                      
            return (dist, -float(size))

        candidates.sort(key=sort_key)
        best = candidates[0]
        return (best[0], best[1])

    def _is_blacklisted(self, x: float, y: float) -> bool:
        r2 = self._blacklist_radius * self._blacklist_radius
        for fx, fy in self._failed_goals:
            if (x - fx) * (x - fx) + (y - fy) * (y - fy) <= r2:
                return True
        return False

    def _find_frontier_cells(self, grid: OccupancyGrid) -> List[GridIndex]:
        width = grid.info.width
        height = grid.info.height
        data = grid.data
        frontiers: List[GridIndex] = []

        def cell(ix: int, iy: int) -> int:
            return int(data[iy * width + ix])

        def is_free(val: int) -> bool:
            return 0 <= val < self.FREE_MAX

        def is_unknown(val: int) -> bool:
            return val == self.UNKNOWN

        for iy in range(height):
            row = iy * width
            for ix in range(width):
                val = int(data[row + ix])
                if not is_free(val):
                    continue
                                                         
                found_unknown = False
                for dy in (-1, 0, 1):
                    ny = iy + dy
                    if ny < 0 or ny >= height:
                        continue
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx = ix + dx
                        if nx < 0 or nx >= width:
                            continue
                        if is_unknown(cell(nx, ny)):
                            found_unknown = True
                            break
                    if found_unknown:
                        break
                if found_unknown:
                    frontiers.append((ix, iy))
        return frontiers

    def _cluster_frontiers(self, frontiers: Sequence[GridIndex]) -> List[List[GridIndex]]:
        """Connected-components (8-connected) via BFS flood-fill."""
        frontier_set = set(frontiers)
        visited = set()
        clusters: List[List[GridIndex]] = []

        for seed in frontiers:
            if seed in visited:
                continue
            cluster: List[GridIndex] = []
            q: deque[GridIndex] = deque([seed])
            visited.add(seed)
            while q:
                cx, cy = q.popleft()
                cluster.append((cx, cy))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        n = (cx + dx, cy + dy)
                        if n in frontier_set and n not in visited:
                            visited.add(n)
                            q.append(n)
            clusters.append(cluster)
        return clusters

    def _cluster_centroid_world(
        self,
        grid: OccupancyGrid,
        cluster: Sequence[GridIndex],
    ) -> Tuple[float, float]:
        mx = sum(c[0] for c in cluster) / float(len(cluster))
        my = sum(c[1] for c in cluster) / float(len(cluster))
        return self._map_to_world(grid, mx, my)

    @staticmethod
    def _map_to_world(grid: OccupancyGrid, mx: float, my: float) -> Tuple[float, float]:
        res = grid.info.resolution
        ox = grid.info.origin.position.x
        oy = grid.info.origin.position.y
                      
        wx = ox + (mx + 0.5) * res
        wy = oy + (my + 0.5) * res
        return (wx, wy)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = FrontierExplorerNode()
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
