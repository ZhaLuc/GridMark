# Package: robot_slam

## Purpose

Configure and launch **slam_toolbox** in **online async** mapping mode, and publish the static `base_link`→`lidar_link` transform so `/scan` is expressed correctly in the robot TF tree.

## Location

`robot_ws/src/robot_slam/`

| Artifact | Role |
| --- | --- |
| `config/slam_toolbox_params.yaml` | Mapper parameters |
| `launch/slam.launch.py` | Includes `slam_toolbox/online_async_launch.py` + static TF |

## Responsibilities

- Consume `/scan` and TF `odom`→`base_link`. 
- Publish `/map` and TF `map`→`odom`. 
- Expose lidar mount offsets as launch arguments.

## Why online async

Async mode processes scans without blocking the sensor callback path as aggressively as sync mode - better for CPU-limited Jetson while driving.

## Key parameters (see YAML for full set)

Motion gates (`minimum_travel_distance` 0.2 m, `minimum_travel_heading` 0.2 rad) reduce graph growth when stationary. `use_scan_matching true` corrects short-term odom error. `max_laser_range` 12 m matches RPLIDAR A2 class range (**datasheet reference**).

## Assumptions

- `frame_id` on LaserScan is `lidar_link` (or consistent with static TF child). 
- Odom quality is good enough that walls are not hopelessly smeared (see build phases).

## Failure modes

| Symptom | Cause |
| --- | --- |
| Empty `/map` | No `/scan`, bad TF, or SLAM not activated |
| Smeared walls | Odom calibration, not “random SLAM bug” |
| TF lookup timeouts | `transform_timeout`; bridge/lidar not running |

## Related

- [Mapping workflow](../workflows/mapping.md) 
- [LiDAR wiring](../hardware/wiring/lidar-and-camera-wiring.md) 
