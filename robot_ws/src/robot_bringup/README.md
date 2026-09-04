# robot_bringup

Top-level launch files that start the full GridMark stack in a
safe order (bridge → LiDAR → wait `/odom`+`/scan` → SLAM → wait `/map` →
Nav2 / perception / frontier explorer / mission).

```bash
ros2 launch robot_bringup full_system.launch.py
```
