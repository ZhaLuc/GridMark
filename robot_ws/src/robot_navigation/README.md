# robot_navigation

Nav2 configuration for differential-drive navigation on the live slam_toolbox `/map`, plus a frontier exploration node.

## Launch Nav2

Requires slam_toolbox (or another source) already publishing `/map` and `map` → `odom`, plus `/scan`, `/odom`, and `odom` → `base_link`.

```bash
ros2 launch robot_navigation navigation.launch.py
```

## Frontier exploration

```bash
ros2 run robot_navigation frontier_explorer_node
```

When no frontiers remain, the node logs `Exploration complete` and publishes `std_msgs/Bool` `data: true` on `/exploration_complete`.

The ~0.25 m × 0.20 m footprint in `config/nav2_params.yaml` is a typical 4WD smart-car size - measure your chassis and update the polygon before relying on clearance.
