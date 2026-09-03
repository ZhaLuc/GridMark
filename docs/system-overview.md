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
