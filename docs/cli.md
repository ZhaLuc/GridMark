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
ros2 topic echo /odom --once
ros2 topic hz /scan
ros2 topic echo /detections
ros2 run tf2_ros tf2_echo map base_link
ros2 run tf2_tools view_frames # writes frames.pdf
```

### Teleop (mapping / odom tests)

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Manual cmd_vel

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" -r 10
```

## Arduino serial (no ROS)

Open serial monitor @ 115200:

```text
L80 R80
L0 R0
L100 R-100
```

Expect continuous:

```text
ODOM <dL> <dR> <dt_ms>
```

## Build / clean

```bash
cd robot_ws
colcon build --symlink-install
colcon build --packages-select robot_bridge robot_mission
rm -rf build install log # full clean
```

## Related

- [Workflows/bringup](workflows/bringup.md) 
- [Troubleshooting](troubleshooting.md) 
