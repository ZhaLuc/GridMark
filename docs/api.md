# API Reference: Topics, TF, and Serial Protocol

Canonical interfaces between packages. **Do not rename these topics** without updating every subscriber/publisher and this document.

## ROS topics

| Topic | Type | Direction | Producer | Consumers |
| --- | --- | --- | --- | --- |
| `/scan` | `sensor_msgs/LaserScan` | out | `rplidar_ros` | slam_toolbox, Nav2 costmaps |
| `/odom` | `nav_msgs/Odometry` | out | `serial_bridge_node` | slam_toolbox, Nav2, RViz |
| `/cmd_vel` | `geometry_msgs/Twist` | in→bridge | Nav2, teleop, mission (zeros) | `serial_bridge_node` |
| `/map` | `nav_msgs/OccupancyGrid` | out | `slam_toolbox` | Nav2 static layer, frontier, mission |
| `/image_raw` | `sensor_msgs/Image` | out | `usb_cam` | `yolo_detector_node` |
| `/detections` | `vision_msgs/Detection2DArray` | out | `yolo_detector_node` | `mission_node` |
| `/exploration_complete` | `std_msgs/Bool` | out | `frontier_explorer_node` | `mission_node` (informational) |

### Field semantics (used by this project)

**`/cmd_vel` (`Twist`)** 
- `linear.x` - forward velocity (m/s), body frame 
- `angular.z` - yaw rate (rad/s) 
- `linear.y` ignored (diff-drive)

**`/odom` (`Odometry`)** 
- `header.frame_id` = `odom` 
- `child_frame_id` = `base_link` 
- Pose from mid-point integration of tick deltas 
- Twist `linear.x` / `angular.z` from last interval 
- Covariance diagonals are tuned for Nav2 on this chassis; refine further from ground truth if needed

**`/detections` (`Detection2DArray`)** 
- Each `Detection2D.bbox.center` is `geometry_msgs/Pose2D` in **image pixels** (`x`, `y`, `theta`) 
- `bbox.size_x` / `size_y` - width/height in pixels 
- `results[].hypothesis.class_id` - string class name 
- `results[].hypothesis.score` - confidence 

**`/map` (`OccupancyGrid`)** 
- `-1` unknown, `0` free, `1-100` occupied (typical slam_toolbox usage) 
- Frontier explorer treats `< 50` as free 

## TF frames

| Frame | Meaning |
| --- | --- |
| `map` | World frame fixed by SLAM |
| `odom` | Continuous odometry frame |
| `base_link` | Robot body (X forward, Y left, Z up) |
| `lidar_link` | LiDAR optical / scan frame |
| `camera_link` | Camera mount frame (body axes; optical conversion inside mission node) |

## Actions

| Action | Type | Client | Server |
| --- | --- | --- | --- |
| `navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | `frontier_explorer_node` | Nav2 `bt_navigator` |

Mission cancels goals via `navigate_to_pose/_action/cancel_goal` (`action_msgs/srv/CancelGoal`).

## USB serial protocol (Jetson ↔ Mega)

**Settings:** 115200 8N1, device typically `/dev/ttyACM0`.

### Jetson → Mega (commands)

```text
L<pwm> R<pwm>\n
```

- `pwm` ∈ [−255, 255] (integer) 
- Positive: RPWM = |pwm|, LPWM = 0, EN high 
- Negative: LPWM = |pwm|, RPWM = 0, EN high 
- Zero: EN low, both PWM 0 
- Optional spaces: `L 80 R -40` also accepted by firmware `sscanf`

**Safety:** If no valid command for **500 ms**, firmware stops both sides.

### Mega → Jetson (odometry stream)

```text
ODOM <left_ticks_delta> <right_ticks_delta> <dt_ms>\n
```

- Emitted every **20 ms** (50 Hz) 
- Deltas are signed longs from quadrature state-machine decoding 
- Bridge integrates; firmware also computes `v`/`ω` locally for Phase 2 diagnostics but does **not** put them on the wire

## QoS notes

| Topic | QoS used in this repo |
| --- | --- |
| `/odom`, `/cmd_vel` (bridge) | Reliable, depth 10 |
| `/map` (frontier, mission) | Reliable + **transient local**, depth 1 |
| `/image_raw` (YOLO) | Best effort, depth 1 |

Mismatch (e.g. subscribing Reliable to Best Effort camera) can yield no callbacks - keep camera QoS best-effort on the detector.

## Related

- [Configuration](configuration.md) 
- [Architecture](architecture.md) 
