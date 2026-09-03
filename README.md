<div align="center">

# GridMark

**Map · Explore · Detect · Mark**

Autonomous indoor SLAM robot - Jetson Orin Nano Super · Arduino Mega 2560

[![License: MIT](https://img.shields.io/github/license/LucasZhang3/SLAM)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/LucasZhang3/SLAM)](https://github.com/LucasZhang3/SLAM/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/LucasZhang3/SLAM)](https://github.com/LucasZhang3/SLAM)
[![GitHub top language](https://img.shields.io/github/languages/top/LucasZhang3/SLAM)](https://github.com/LucasZhang3/SLAM)

</div>

## About

**GridMark** is a differential-drive indoor robot that builds a LiDAR occupancy map, explores unknown space with Nav2, detects a configured target with YOLO26 (TensorRT on Orin), and stops to mark the target's map-frame location. The stack runs on an NVIDIA Jetson Orin Nano Super with an Arduino Mega 2560 handling motors and encoders over USB serial.

This repository is the complete project: Mega firmware, ROS 2 Jazzy packages, trained detector weights, wiring schematics, operating captures, and field validation records.

### Gallery

<p align="center">
  <img src="docs/images/robot/robot-hero.jpg" alt="GridMark on the test track with LiDAR and arm" width="780" />
  <br />
  <em>GridMark on the lab track - multi-deck chassis, RPLIDAR, and manipulator arm</em>
</p>

<p align="center">
  <img src="docs/images/features/feature-robot-operating.jpg" alt="GridMark on the full arena mat" width="780" />
  <br />
  <em>Field arena overview - autonomous run on the taped course with LED path markers</em>
</p>

<table>
  <tr>
    <td align="center" width="50%">
      <img src="docs/images/robot/robot-top-view.jpg" alt="Top-down chassis and gripper" width="100%" />
      <br />
      <em>Top-down deck - chassis plates and open gripper</em>
    </td>
    <td align="center" width="50%">
      <img src="docs/images/robot/robot-sensors-mount.jpg" alt="LiDAR and arm sensor deck" width="100%" />
      <br />
      <em>Sensor deck - LiDAR puck and arm mount</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
