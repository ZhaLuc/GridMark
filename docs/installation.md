# Installation

This guide installs the software stack on a **NVIDIA Jetson Orin Nano Super Developer Kit** running **JetPack 6.x / Ubuntu 22.04** with **ROS 2 Jazzy**. Hardware assembly is covered in [hardware](hardware/README.md) and [build-phases](build-phases.md).

## Prerequisites

| Requirement | Notes |
| --- | --- |
| Jetson Orin Nano Super Developer Kit | JetPack 6.x image flashed |
| Network access | `apt`, ROS packages, optional pip wheels |
| Arduino IDE or `arduino-cli` | To flash `robot_firmware.ino` |
| USB cables | Mega USB-B; LiDAR/camera via **powered hub** |
| Disk space | ROS 2 + Nav2 + slam_toolbox + TensorRT + models |

## 1. System packages (Ubuntu)

```bash
sudo apt update
sudo apt install -y \
  python3-pip python3-serial python3-pil \
  git curl build-essential
```

Add your user to the serial group (re-login required):

```bash
sudo usermod -aG dialout $USER
```

## 2. ROS 2 Jazzy

Follow the official ROS 2 Jazzy installation for Ubuntu 22.04, then:

```bash
sudo apt install -y \
  ros-jazzy-desktop \
  ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-cv-bridge \
  ros-jazzy-vision-msgs \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-geometry-msgs \
  ros-jazzy-usb-cam \
  ros-jazzy-rplidar-ros \
  python3-colcon-common-extensions
```

> **Note:** Exact `apt` package names for `rplidar-ros` / `usb-cam` can vary by vendor overlay. If a package is missing, install from the upstream ROS 2 package source or Slamtec’s `rplidar_ros` repository and adjust `full_system.launch.py` if the executable name differs (`rplidar_node` vs composition).

Source ROS in every terminal:

```bash
source /opt/ros/jazzy/setup.bash
```

## 3. Clone and build this workspace

```bash
git clone https://github.com/LucasZhang3/SLAM.git
cd SLAM/robot_ws
rosdep update
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

### What `colcon build` compiles

| Package | Build type | Output |
| --- | --- | --- |
| `robot_bridge` | ament_python | `serial_bridge_node` |
| `robot_slam` | ament_cmake | share launch/config |
| `robot_navigation` | ament_python | `frontier_explorer_node` + Nav2 params |
| `robot_perception` | ament_python | `yolo_detector_node` |
| `robot_mission` | ament_python | `mission_node` |
| `robot_bringup` | ament_cmake | `full_system.launch.py` |
| `robot_firmware` | - | Not built by colcon; flash with Arduino tools |

## 4. Python ML dependencies (Jetson)

On the Orin, install Ultralytics in an environment compatible with your JetPack PyTorch/TensorRT build:

```bash
pip3 install ultralytics
```

Train/export a YOLO26 model to TensorRT as described in [`robot_perception/models/README.md`](../robot_ws/src/robot_perception/models/README.md). Place the `.engine` where launch expects it (package share `models/` or `weights_path:=...`).

## 5. Flash Arduino firmware

1. Open `robot_ws/src/robot_firmware/robot_firmware.ino` in Arduino IDE. 
2. Board: **Arduino Mega or Mega 2560**. 
3. Update `TICKS_PER_REVOLUTION`, `WHEEL_RADIUS_M`, `TRACK_WIDTH_M` after measuring (see encoder wiring). 
4. Upload via USB. 
5. Serial monitor @ **115200**: send `L80 R80` then `L0 R0` to verify motion.

## 6. Verify installation (package smoke test)

After `colcon build`, confirm packages are discoverable (serial may error if the Mega is unplugged):

```bash
source /opt/ros/jazzy/setup.bash
source robot_ws/install/setup.bash
ros2 pkg list | grep robot_
ros2 launch robot_bridge bridge.launch.py # expects serial device; may error if absent
```

## Assumptions

- You are on aarch64 Jetson Ubuntu 22.04, not a generic x86 laptop (TensorRT engines are device-specific). 
- `rosdep` can resolve declared dependencies; some pip packages (`ultralytics`) remain manual.

## Common install failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Permission denied` on `/dev/ttyACM0` | Not in `dialout` | `usermod` + re-login |
| `Package 'rplidar_ros' not found` | Distro package name | Install upstream; edit bringup executable |
| `ultralytics` import fails | Wrong Python / missing CUDA wheel | Use Jetson-compatible PyTorch then ultralytics |
| `colcon` can’t find `vision_msgs` | Incomplete ROS install | `sudo apt install ros-jazzy-vision-msgs` |

## Next steps

- Wire hardware: [hardware/README.md](hardware/README.md) 
- Follow [build-phases.md](build-phases.md) 
- Configure parameters: [configuration.md](configuration.md) 
