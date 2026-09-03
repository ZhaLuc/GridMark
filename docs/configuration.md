# Configuration Reference

All tunable parameters that ship with this repository. Defaults marked  were measured on the assembled chassis before navigation and mission validation.

## Configuration files

| File | Package | Purpose |
| --- | --- | --- |
| `robot_bridge/config/odom_calibration.yaml` | robot_bridge | Serial port, kinematics, PWM scale |
| `robot_slam/config/slam_toolbox_params.yaml` | robot_slam | Online async SLAM |
| `robot_navigation/config/nav2_params.yaml` | robot_navigation | Nav2 stack |
| `robot_perception/config/usb_cam_params.yaml` | robot_perception | Camera device / resolution |
| Firmware constants in `.ino` | robot_firmware | Must stay synced with odom YAML |

## robot_bridge (`serial_bridge_node`)

| Parameter | Default | Meaning |
| --- | --- | --- |
| `serial_port` | `/dev/ttyACM0` | Mega USB device |
| `baud_rate` | `115200` | Must match firmware |
| `ticks_per_revolution` | `1440.0` | **Measure** |
| `wheel_radius_m` | `0.0325` | **Measure** |
| `track_width_m` | `0.20` | **Measure** |
| `max_wheel_speed_mps` | `0.6` | Speed that maps to PWM 255 |
| `cmd_send_hz` | `20.0` | Command write rate |
| `odom_frame` | `odom` | TF parent |
| `base_frame` | `base_link` | TF child |

**Inverse kinematics used:** 
`v_l = v − ω·L/2`, `v_r = v + ω·L/2`, then `pwm = clamp(round(v_wheel / max_wheel_speed_mps · 255))`.

## robot_firmware (compile-time)

| Constant | Default | Meaning |
| --- | --- | --- |
| `TICKS_PER_REVOLUTION` | 1440 | Encoder counts / rev (x4 decode) |
| `WHEEL_RADIUS_M` | 0.0325 | Wheel radius (m) |
| `TRACK_WIDTH_M` | 0.20 | Track width (m) |
| `CONTROL_DT_MS` | 20 | Loop / ODOM period |
| `CMD_TIMEOUT_MS` | 500 | Stop if no serial command |

## robot_slam launch arguments

| Argument | Default | Meaning |
| --- | --- | --- |
| `lidar_x` | `0.10` | base→lidar X (m) |
| `lidar_y` | `0.00` | Y (m) |
| `lidar_z` | `0.15` | Z (m) |
| `lidar_yaw/pitch/roll` | `0.0` | rad |
| `slam_params_file` | package YAML | slam_toolbox params |
| `use_sim_time` | `false` | `/clock` |

### Notable slam_toolbox parameters

| Parameter | Value in repo | Why |
| --- | --- | --- |
| `mode` | `mapping` | Online map building |
| `scan_topic` | `/scan` | Contract |
| `base_frame` | `base_link` | Contract |
| `resolution` | `0.05` | 5 cm cells |
| `max_laser_range` | `12.0` | RPLIDAR A2 class range (datasheet reference) |
| `minimum_travel_distance` | `0.2` | Motion gate (m) |
| `minimum_travel_heading` | `0.2` | Motion gate (rad) |
| `transform_timeout` | `0.3` | TF wait (s) |
| `use_scan_matching` | `true` | Correct short-term odom |

## Nav2 (`nav2_params.yaml`) highlights

| Setting | Value | Notes |
| --- | --- | --- |
| Controller | Regulated Pure Pursuit | Diff-drive appropriate |
| Footprint | ±0.125 m × ±0.10 m | ~25×20 cm measured bumper outline |
| Inflation radius | 0.35 m | Both costmaps |
| Obstacle source | `/scan` | Local + global |
| Static map | `/map` | From slam_toolbox |
| `allow_unknown` | `true` | Needed for frontier goals |

## robot_perception

| Parameter | Default | Meaning |
| --- | --- | --- |
| `weights_path` | `models/target_object_n.engine` | TensorRT engine |
| `confidence_threshold` | `0.6` | Filter |
| `inference_hz` | `8.0` | GPU sharing with SLAM/Nav2 |
| `image_topic` | `/image_raw` | Input |
| `detections_topic` | `/detections` | Output |
| `device` | `0` | CUDA device |
| `class_names` | `[""]` | Empty = all classes |

`usb_cam`: `/dev/video0`, 640×480, `frame_id`=`camera_link`.

## robot_mission

| Parameter | Default | Meaning |
| --- | --- | --- |
| `target_class` | `target_object` | Must match YOLO class id string |
| `confidence_threshold` | `0.6` | Per detection |
| `consecutive_required` | `3` | Anti-false-positive gate |
| `fx,fy,cx,cy` | 600,600,320,240 | Pinhole intrinsics (**calibrate**) |
| `target_height_m` | `0.05` | Ground-plane intersection height |
| `assumed_range_m` | `1.5` | Fallback range along ray |
| `use_depth` | `false` | Optional RealSense path |
| `depth_topic` | `/camera/aligned_depth_to_color/image_raw` | If `use_depth` |
| `output_dir` | `mission_outputs` | Annotated PNG directory |

## robot_bringup launch arguments

| Argument | Default |
| --- | --- |
| `serial_port` | `/dev/ttyACM0` (documented; bridge YAML still primary) |
| `lidar_port` | `/dev/ttyUSB0` |
| `lidar_x/y/z` | `0.10` / `0.00` / `0.15` |
| `camera_x/y/z` | `0.12` / `0.00` / `0.20` |
| `use_sim_time` | `false` |

## Sync rules

1. Firmware geometry constants **must** match `odom_calibration.yaml`. 
2. LiDAR TF launch args **must** match measured mounts and wiring docs once measured. 
3. YOLO `class_id` strings **must** match `mission_node.target_class`. 

## Related

- [CLI](cli.md) 
- [Installation](installation.md) 
