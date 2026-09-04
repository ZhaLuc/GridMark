# robot_slam

slam_toolbox online-async configuration and launch for mapping (`/map`, `map` → `odom`), plus the static `base_link` → `lidar_link` transform.

## Run

```bash
ros2 launch robot_slam slam.launch.py
```

Override the example LiDAR mount after measuring the real robot:

```bash
ros2 launch robot_slam slam.launch.py lidar_x:=0.10 lidar_y:=0.0 lidar_z:=0.15 lidar_yaw:=0.0
```

Defaults match the measured offsets in `docs/hardware/wiring/lidar-and-camera-wiring.md` (calibrated mount offsets).
