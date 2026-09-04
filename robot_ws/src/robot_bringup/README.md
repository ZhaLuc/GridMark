# robot_bringup

Top-level launch files that start the full GridMark stack in a
safe order (bridge → LiDAR → wait `/odom`+`/scan` → SLAM → wait `/map` →
