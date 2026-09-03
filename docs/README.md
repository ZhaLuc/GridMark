# Documentation Index

Welcome to the **GridMark** documentation. This suite covers the firmware, ROS 2 workspace, trained YOLO26 weights, hardware wiring, and field validation for the completed differential-drive robot: LiDAR SLAM, Nav2 frontier exploration, TensorRT detection, and map-frame target marking.

## How to read these docs

| Audience | Start here |
| --- | --- |
| First-time builder | [Installation](installation.md) → [Hardware](hardware/README.md) → [Build phases](build-phases.md) |
| Software engineer | [System overview](system-overview.md) → [Architecture](architecture.md) → [Packages](packages/README.md) |
| Integrator / DevOps | [Configuration](configuration.md) → [CLI & launch](cli.md) → [API / topics](api.md) |
| Security reviewer | [Security](security.md) |
| Performance tuner | [Performance](performance.md) → [Troubleshooting](troubleshooting.md) |

## Table of contents

### Foundations

| Document | Description |
| --- | --- |
| [System overview](system-overview.md) | Mission, capabilities, stack, design philosophy |
| [Architecture](architecture.md) | Components, data/control flow, TF tree, startup gates |
| [Installation](installation.md) | Jetson, ROS 2 Jazzy, workspace build, dependencies |
| [Configuration](configuration.md) | All ROS parameters, YAML files, launch arguments |
| [CLI & launch reference](cli.md) | Commands to run each subsystem and the full stack |
| [API: topics, TF, serial](api.md) | Message contracts, frames, USB serial protocol |

### Packages (software modules)

| Document | Package |
| --- | --- |
| [Packages index](packages/README.md) | Map of `robot_ws/src` |
| [robot_bringup](packages/robot_bringup.md) | Ordered full-system launch |
| [robot_firmware](packages/robot_firmware.md) | Arduino Mega sketch |
| [robot_bridge](packages/robot_bridge.md) | Serial ↔ `/cmd_vel` / `/odom` |
| [robot_slam](packages/robot_slam.md) | slam_toolbox + lidar TF |
| [robot_navigation](packages/robot_navigation.md) | Nav2 + frontier explorer |
| [robot_perception](packages/robot_perception.md) | usb_cam + YOLO26 TensorRT |
| [robot_mission](packages/robot_mission.md) | Detect → stop → annotate map |

### Workflows

| Document | Description |
| --- | --- |
| [Bringup workflow](workflows/bringup.md) | Cold start to healthy topics |
| [Mapping workflow](workflows/mapping.md) | Teleop / online SLAM |
| [Exploration workflow](workflows/exploration.md) | Frontier → NavigateToPose |
| [Detection & mission](workflows/detection-mission.md) | YOLO → mission stop |

### Hardware & verification

| Document | Description |
| --- | --- |
| [Hardware index](hardware/README.md) | BOM and wiring |
| [Images and schematics](images/README.md) | Robot visuals and rendered wiring schematics |
| [Build phases 1-5](build-phases.md) | Step-by-step physical/software bring-up |
| [Verification checklist](verification-checklist.md) | Pass/fail field tests |
| [Field test log](field-test-log.md) | Bring-up and mission validation records |

### Engineering practice

| Document | Description |
| --- | --- |
| [Development](development.md) | Workspace layout, coding conventions, extending |
| [Troubleshooting](troubleshooting.md) | Symptom → cause → fix |
| [Security](security.md) | Power, LiPo, USB, network, model supply chain |
| [Performance](performance.md) | Orin Nano budgets, rate limits, costmaps |
| [Contributing](contributing.md) | How to change this repo safely |
| [FAQ](faq.md) | Common questions |
| [Glossary](glossary.md) | Terms and abbreviations |

## Topic / TF contract (quick reference)

| Topic | Type |
| --- | --- |
| `/scan` | `sensor_msgs/LaserScan` |
| `/odom` | `nav_msgs/Odometry` |
| `/cmd_vel` | `geometry_msgs/Twist` |
| `/map` | `nav_msgs/OccupancyGrid` |
| `/image_raw` | `sensor_msgs/Image` |
| `/detections` | `vision_msgs/Detection2DArray` |
| `/exploration_complete` | `std_msgs/Bool` |

TF: `map` → `odom` → `base_link` → `{lidar_link, camera_link}`

See [api.md](api.md) for full semantics.
