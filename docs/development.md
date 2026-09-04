# Development Guide

## Workspace layout

Standard ROS 2 workspace under `robot_ws/`. Documentation lives in `/docs` at the repo root (sibling to `robot_ws`), not inside `src`.

## Coding conventions

| Area | Convention |
| --- | --- |
| Nodes | Python `rclpy` unless C++ requested |
| Topics | Absolute names per [api.md](api.md) |
| Packages | `ament_python` for nodes; `ament_cmake` for launch-only |
| Measurements | Keep calibration YAML and field-test log in sync |
| Commits | Clear, human-readable messages |

## Adding a node

1. Create/extend package with `package.xml`, `setup.py`, entry point. 
2. Document topics in `docs/api.md` and package page. 
3. Wire into `full_system.launch.py` only if startup order is defined. 
4. Update configuration tables.

## Testing approach (this repo)

There is **no** automated hardware-in-the-loop CI in-tree. Verification is manual per [verification-checklist.md](verification-checklist.md). Optional future work: unit tests for frontier clustering and kinematics with synthetic grids/ticks.

## Build process

```bash
cd robot_ws
colcon build --symlink-install
source install/setup.bash
```

Firmware: Arduino IDE upload (separate toolchain).

## Extensibility ideas (not implemented)

- IMU fusion on Mega or Jetson 
- Depth camera default for mission 
- Gazebo/Ignition simulation package 
- Lifecycle management for mission/explorer 

## Related

- [Contributing](contributing.md) 
- [Architecture](architecture.md) 
