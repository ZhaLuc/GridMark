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
