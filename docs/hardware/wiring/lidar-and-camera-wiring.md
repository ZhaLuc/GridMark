# LiDAR and Camera Wiring

RPLIDAR A2 and the USB webcam both connect to the **Jetson Orin Nano Super** through a **powered USB hub**. Do **not** plug the LiDAR (and preferably not the camera) directly into a Jetson root USB port for this project’s default configuration - shared bandwidth and port power budgeting are a common failure mode (“where people get stuck”: intermittent `/scan`, USB resets, or camera stalls when SLAM and YOLO run together).

## Schematic and mount reference

![LiDAR and camera USB schematic](../../images/schematics/schematic-lidar-camera.png)

![Sensor mount visual reference](../../images/robot/robot-sensors-mount.jpg)

## USB topology

| Device | Connection | Host path |
| --- | --- | --- |
| Powered USB hub | Upstream cable | Jetson USB host port |
| Powered USB hub | External power supply | Hub’s own DC input (required - do not run hub bus-powered only) |
| RPLIDAR A2 | USB adapter board → USB-A cable | **Powered hub** downstream port |
| USB webcam | USB-A cable | **Powered hub** downstream port |

The hub’s upstream link carries data to the Jetson; the hub PSU supplies device current so the Jetson port is not asked to source LiDAR motor + camera power.

## Plain-text pin / connection table

| Component | Pin / port | Connects to |
| --- | --- | --- |
| RPLIDAR A2 | Interface cable | Official USB adapter board (as supplied with A2 kits) |
| RPLIDAR USB adapter | USB-A plug | Powered USB hub port 1 |
| USB webcam | USB-A plug | Powered USB hub port 2 |
| Powered USB hub | Upstream USB | Jetson Orin Nano Super USB host |
| Powered USB hub | DC power input | Hub manufacturer’s rated supply (or suitable regulated output) |
| Jetson | USB host | Hub upstream only (for these sensors) |

ROS expectations once enumerated on Linux:

- LiDAR → `rplidar_ros` → `/scan` (`sensor_msgs/LaserScan`) 
- Camera → `usb_cam` → `/image_raw` (`sensor_msgs/Image`)

## Physical mounting and static TF frames

The TF tree for this project includes:
