# System Overview

## What this project is

**GridMark** is a completed **4WD differential-drive** indoor platform. The robot:

1. Drives under ROS 2 velocity commands.
2. Estimates wheel odometry from quadrature encoders.
3. Maps the environment online with a 2D LiDAR (`slam_toolbox`).
4. Explores unknown space with Nav2 + a frontier explorer.
5. Detects a configured visual target with YOLO26 (TensorRT on Orin).
6. Stops, cancels navigation, and saves an annotated occupancy-map PNG when the target is confirmed.

This repository contains the Arduino firmware, ROS 2 packages, trained detector weights, launch orchestration, hardware wiring documentation, and field validation records from the build.

## Purpose

| Goal | How this repo addresses it |
| --- | --- |
| Reproducible design | Pin tables, Mermaid schematics, BOM, fixed topic/TF contract |
| Separable bring-up | Phased build guide (chassis → odom → bridge → LiDAR → SLAM → Nav2 → vision → mission) |
| Safe defaults | Motor command timeout, powered USB hub guidance, GPU rate-limited inference |
| Auditable math | Documented differential-drive kinematics and bearing projection |

## Design philosophy

1. **Compute isolation** - Motor power (3S LiPo → BTS7960) is electrically separate from Jetson 5 V (buck). Shared rails brown out under stall current.
2. **Thin MCU, thick SBC** - The Mega runs a tight 50 Hz loop (PWM + tick deltas). Heavier float odometry integration and SLAM/Nav2/YOLO run on the Jetson.
3. **One topic contract** - All packages agree on `/scan`, `/odom`, `/cmd_vel`, `/map`, `/image_raw`, `/detections`, and the TF tree.
4. **Calibrated geometry** - Encoder ticks, wheel radius, track width, and sensor TFs measured on the chassis.
5. **Fail safe on link loss** - If Jetson↔Mega serial stalls >500 ms, firmware zeroes motors.

## Core features

- Dual-BTS7960 side drive with signed PWM serial commands
- Quadrature ISR decoding on Mega interrupt pins
- ROS 2 Jazzy `serial_bridge_node` (`/cmd_vel` ↔ `/odom` + `odom`→`base_link`)
- `slam_toolbox` online async mapping (`/map`, `map`→`odom`)
- Nav2 with Regulated Pure Pursuit + custom frontier explorer
- `usb_cam` + Ultralytics YOLO26 TensorRT detector at capped Hz
- Mission node: consecutive detections → map estimate → stop + PNG

## Technology stack

| Layer | Technology | Role |
| --- | --- | --- |
| High-level compute | NVIDIA Jetson Orin Nano Super, JetPack 6.x, Ubuntu 22.04 | ROS 2, SLAM, Nav2, TensorRT |
| Low-level control | Arduino Mega 2560 | Motors, encoders, serial protocol |
| Middleware | ROS 2 Jazzy Jalisco | Topics, TF, actions, launch |
| SLAM | slam_toolbox (online async) | Occupancy mapping |
| Navigation | Nav2 + frontier explorer | Autonomous coverage |
| Perception | Ultralytics YOLO26-nano → ONNX / TensorRT | Target detection |
| LiDAR | RPLIDAR A2 | `/scan` |
| Drive | BTS7960 ×2, 4WD + encoders | Motion + odometry |

## Operating captures

| View | Asset |
| --- | --- |
| Chassis (top-down) | [docs/images/robot/robot-top-view.jpg](images/robot/robot-top-view.jpg) |
| Hero / track | [docs/images/robot/robot-hero.jpg](images/robot/robot-hero.jpg) |
| Online SLAM (RViz) | [docs/images/features/feature-slam-map-rviz.jpg](images/features/feature-slam-map-rviz.jpg) |
| 3D map view | [docs/images/features/feature-slam-map-3d.jpg](images/features/feature-slam-map-3d.jpg) |
| Field operation | [docs/images/features/feature-robot-operating.jpg](images/features/feature-robot-operating.jpg) |
| Gripper / mission hardware | [docs/images/features/feature-gripper-top.jpg](images/features/feature-gripper-top.jpg) |
| Annotated mission map | [docs/images/features/feature-annotated-mission-map.jpg](images/features/feature-annotated-mission-map.jpg) |

## Related

- [Architecture](architecture.md)
- [Field test log](field-test-log.md)
- [Hardware](hardware/README.md)
