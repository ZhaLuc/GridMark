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

