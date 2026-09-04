# robot_navigation

Nav2 configuration for differential-drive navigation on the live slam_toolbox `/map`, plus a frontier exploration node.

## Launch Nav2

Requires slam_toolbox (or another source) already publishing `/map` and `map` → `odom`, plus `/scan`, `/odom`, and `odom` → `base_link`.

```bash
ros2 launch robot_navigation navigation.launch.py
