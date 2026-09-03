# Configuration Reference

All tunable parameters that ship with this repository. Defaults marked  were measured on the assembled chassis before navigation and mission validation.

## Configuration files

| File | Package | Purpose |
| --- | --- | --- |
| `robot_bridge/config/odom_calibration.yaml` | robot_bridge | Serial port, kinematics, PWM scale |
| `robot_slam/config/slam_toolbox_params.yaml` | robot_slam | Online async SLAM |
| `robot_navigation/config/nav2_params.yaml` | robot_navigation | Nav2 stack |
| `robot_perception/config/usb_cam_params.yaml` | robot_perception | Camera device / resolution |
| Firmware constants in `.ino` | robot_firmware | Must stay synced with odom YAML |

## robot_bridge (`serial_bridge_node`)

| Parameter | Default | Meaning |
| --- | --- | --- |
| `serial_port` | `/dev/ttyACM0` | Mega USB device |
| `baud_rate` | `115200` | Must match firmware |
| `ticks_per_revolution` | `1440.0` | **Measure** |
| `wheel_radius_m` | `0.0325` | **Measure** |
| `track_width_m` | `0.20` | **Measure** |
| `max_wheel_speed_mps` | `0.6` | Speed that maps to PWM 255 |
| `cmd_send_hz` | `20.0` | Command write rate |
| `odom_frame` | `odom` | TF parent |
| `base_frame` | `base_link` | TF child |

**Inverse kinematics used:** 
`v_l = v − ω·L/2`, `v_r = v + ω·L/2`, then `pwm = clamp(round(v_wheel / max_wheel_speed_mps · 255))`.

## robot_firmware (compile-time)

| Constant | Default | Meaning |
| --- | --- | --- |
| `TICKS_PER_REVOLUTION` | 1440 | Encoder counts / rev (x4 decode) |
| `WHEEL_RADIUS_M` | 0.0325 | Wheel radius (m) |
| `TRACK_WIDTH_M` | 0.20 | Track width (m) |
| `CONTROL_DT_MS` | 20 | Loop / ODOM period |
| `CMD_TIMEOUT_MS` | 500 | Stop if no serial command |
