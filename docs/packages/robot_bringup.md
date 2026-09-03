# Package: robot_bringup

## Purpose

Top-level orchestration so operators can start the full stack in a **safe order** with topic readiness gates. Without gating, `slam_toolbox` and Nav2 often start before `/scan`, `/odom`, or `/map` exist.

## Location

`robot_ws/src/robot_bringup/`

| Path | Role |
| --- | --- |
| `launch/full_system.launch.py` | Ordered bringup |
| `package.xml` / `CMakeLists.txt` | ament_cmake; installs `launch/` |

## Responsibilities

1. Launch `robot_bridge`. 
2. After 2 s, start `rplidar_ros` `rplidar_node`. 
3. Wait until `/odom` and `/scan` appear in `ros2 topic list`. 
4. Include `robot_slam/slam.launch.py`. 
5. Wait until `/map` appears. 
6. Include Nav2 + perception; publish `base_link`→`camera_link` static TF. 
7. After 5 s more, start `frontier_explorer_node` and `mission_node`.

## Internal logic (gates)

Wait scripts are `ExecuteProcess` bash loops:

```bash
until ros2 topic list | grep -Fxq "/odom"; do sleep 1; done
```

`RegisterEventHandler(OnProcessExit)` starts the next stage when the wait process exits. Timeouts: 120 s for odom/scan, 180 s for map.

## Inputs / outputs

| In | Out |
| --- | --- |
| Launch arguments (`lidar_*`, `camera_*`, ports) | Running graph of nodes |
| Assumes `bash` + sourced ROS env in the process environment | Log lines tagged `[bringup]` |

## Dependencies

Exec depends: `robot_bridge`, `robot_slam`, `robot_navigation`, `robot_perception`, `robot_mission`, `rplidar_ros`, `tf2_ros`, launch stack.

## Assumptions

- `rplidar_node` executable exists (adjust if your distro uses composition). 
- Bridge YAML already points at the correct `serial_port`. 
- OnProcessExit fires even on wait **failure** (timeout exit 1) - operator must watch logs.

## Limitations & failure modes

| Issue | Effect |
| --- | --- |
| Wait timeout | Downstream stage may still be triggered on exit; check logs |
| Wrong lidar device | `/scan` never appears; gate blocks |
| Missing YOLO engine | Perception starts but detector no-ops; mission never confirms |

## How to run

```bash
ros2 launch robot_bringup full_system.launch.py
```

See [workflows/bringup](../workflows/bringup.md).
