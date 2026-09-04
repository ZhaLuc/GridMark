# Glossary

| Term | Definition |
| --- | --- |
| **base_link** | Robot body frame (X forward, Y left, Z up) |
| **BTS7960** | Dual H-bridge motor driver module (one per side here) |
| **Costmap** | Nav2 occupancy grid for planning/control |
| **Differential drive** | Motion from left/right wheel speeds |
| **Frontier** | Free cell adjacent to unknown space |
| **JetPack** | NVIDIA SDK/OS image for Jetson |
| **Nav2** | ROS 2 Navigation stack |
| **OccupancyGrid** | 2D map message (`nav_msgs`) |
| **Orin Nano Super** | Jetson compute module/kit used here |
| **Quadrature encoder** | A/B channels for direction-aware ticks |
| **RPP** | Regulated Pure Pursuit controller |
| **REP-103** | ROS frame conventions (incl. optical frames) |
| **slam_toolbox** | 2D SLAM package (pose-graph + occupancy) |
| **TensorRT engine** | Optimized inference binary (`.engine`) |
| **TF** | Transform tree (`tf2`) |
| **Tick delta** | Encoder count change over one control interval |
| **Transient local** | QoS durability for latched latched-like topics (e.g. `/map`) |
| **Twist** | Linear + angular velocity message |
| **YOLO26** | Ultralytics detection model family used in this project |
