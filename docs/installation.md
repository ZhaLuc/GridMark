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
