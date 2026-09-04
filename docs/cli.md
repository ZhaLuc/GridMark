# CLI and Launch Reference

Commands assume:

```bash
source /opt/ros/jazzy/setup.bash
source /path/to/SLAM/robot_ws/install/setup.bash
```

## Full stack

```bash
ros2 launch robot_bringup full_system.launch.py
```

Optional overrides:

```bash
ros2 launch robot_bringup full_system.launch.py \
  lidar_port:=/dev/ttyUSB0 \
  lidar_x:=0.10 lidar_y:=0.0 lidar_z:=0.15 \
  camera_x:=0.12 camera_y:=0.0 camera_z:=0.20
```

**What starts (ordered):** bridge → RPLIDAR → wait `/odom`+`/scan` → SLAM → wait `/map` → Nav2 + perception + camera TF → frontier explorer + mission.

## Individual launches

| Command | Package |
| --- | --- |
| `ros2 launch robot_bridge bridge.launch.py` | Serial bridge |
| `ros2 launch robot_slam slam.launch.py` | slam_toolbox + lidar TF |
| `ros2 launch robot_navigation navigation.launch.py` | Nav2 bringup |
| `ros2 launch robot_perception perception.launch.py` | usb_cam + YOLO |
| `ros2 launch robot_mission mission.launch.py` | Mission node |

## Nodes (direct)

```bash
ros2 run robot_bridge serial_bridge_node
ros2 run robot_navigation frontier_explorer_node
ros2 run robot_perception yolo_detector_node --ros-args -p weights_path:=/abs/path/model.engine
ros2 run robot_mission mission_node
```

## Inspection utilities

```bash
ros2 topic list
