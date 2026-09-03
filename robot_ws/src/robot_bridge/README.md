# robot_bridge

ROS 2 package that bridges the Arduino Mega USB serial protocol to `/cmd_vel`, `/odom`, and `odom` → `base_link` TF.

## Run

```bash
ros2 launch robot_bridge bridge.launch.py
```

Calibration parameters live in `config/odom_calibration.yaml` (example / reference values - measure on the physical robot).
